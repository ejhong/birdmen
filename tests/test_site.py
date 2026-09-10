"""Offline integrity checks. No model calls, network requests or historical reanalysis."""
from copy import deepcopy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit
import struct

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
spec = importlib.util.spec_from_file_location("publish", ROOT / "pipeline/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


def jpeg_size(path):
    """Width and height from a JPEG's first frame header; standard library only."""
    data = path.read_bytes()
    assert data[:2] == b"\xff\xd8", path
    i = 2
    while i < len(data):
        assert data[i] == 0xFF, path
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + length
    raise ValueError(f"No frame header: {path}")


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.sections = []
        self.section_stack = []
        self.text = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.sections.append(attrs.get("id"))
            self.section_stack.append(attrs.get("id"))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == "img":
            attrs["section"] = self.section_stack[-1] if self.section_stack else None
            self.images.append(attrs)

    def handle_endtag(self, tag):
        if tag == "section" and self.section_stack:
            self.section_stack.pop()

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "research/civilisers/v2/evidence.json").read_text())
        cls.studies = json.loads((ROOT / "research/investigations.json").read_text())
        cls.pages = {path: Page(path) for path in DOCS.glob("*.html")}

    def test_evidence_integrity(self):
        publish.validate(self.data)
        self.assertEqual(len(self.data["passages"]), 29)
        self.assertEqual(len(self.data["sources"]), 10)
        self.assertEqual(len(self.data["figures"]), 10)
        for source in self.data["sources"]:
            for field in ("composition", "edition", "mediation", "open_questions"):
                self.assertTrue(source[field], (source["id"], field))
            self.assertTrue(source["url"].startswith("https://"))

    def test_duplicate_passage_rejected(self):
        broken = deepcopy(self.data)
        broken["passages"].append(deepcopy(broken["passages"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            publish.validate(broken)

    def test_unsupported_claim_rejected(self):
        broken = deepcopy(self.data)
        broken["figures"][0]["comparison"]["arrival"]["evidence"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            publish.validate(broken)

    def test_wrong_figure_evidence_rejected(self):
        broken = deepcopy(self.data)
        broken["figures"][0]["comparison"]["arrival"]["evidence"] = ["Q1"]
        with self.assertRaisesRegex(ValueError, "Mismatched"):
            publish.validate(broken)

    def test_missing_claim_column_rejected(self):
        broken = deepcopy(self.data)
        del broken["figures"][0]["comparison"]["arrival"]
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            publish.validate(broken)

    def test_published_outputs_are_current(self):
        self.assertEqual(publish.build(check=True), 0)

    def test_all_studies_have_equal_card_structure(self):
        self.assertEqual(len(self.studies), 5)
        self.assertEqual(len({s["id"] for s in self.studies}), 5)
        home = (DOCS / "index.html").read_text()
        self.assertEqual(home.count('class="investigation"'), 5)
        for study in self.studies:
            self.assertIn(f'id="study-{study["id"]}"', home)
            for field in ("question", "finding", "limitations"):
                self.assertTrue(study[field])
            if not study["url"].startswith("https:"):
                page = (DOCS / study["url"]).read_text()
                self.assertEqual(page.count('class="study-review wrap"'), 1)
                self.assertIn('id="limits"', page)

    def test_images_preserve_inputs(self):
        manifest = json.loads((ROOT / "research/images.json").read_text())
        self.assertEqual(len(manifest), 20)
        self.assertEqual(len({item["output"] for item in manifest}), 20)
        self.assertEqual(sum(1 for item in manifest if not item["input"].startswith("fenton/")), 6)
        for item in manifest:
            with self.subTest(image=item["input"]):
                src = ROOT / "inputs" / item["input"]
                dst = DOCS / "img/inputs" / item["output"]
                for field in ("description", "identification", "credit", "section"):
                    self.assertTrue(item[field], field)
                if item.get("crop"):
                    left, top, right, bottom = item["crop"]
                    self.assertTrue(src.is_file())
                    self.assertEqual(jpeg_size(dst), (right - left, bottom - top))
                else:
                    self.assertEqual(src.read_bytes(), dst.read_bytes())

    def test_studies_precede_the_integrated_narrative(self):
        page = self.pages[DOCS / "index.html"]
        self.assertEqual(page.sections[0], "investigations")
        self.assertLess(page.sections.index("investigations"), page.sections.index("pattern"))
        self.assertEqual(page.sections.index("animals"), page.sections.index("handbags") + 1)
        self.assertNotIn("new-comparisons", page.sections)

    def test_reference_images_are_in_their_topics_once(self):
        page = self.pages[DOCS / "index.html"]
        manifest = json.loads((ROOT / "research/images.json").read_text())
        images = [image for image in page.images if image.get("src", "").startswith("img/inputs/")]
        self.assertEqual(len(images), len(manifest))
        by_src = {image["src"]: image for image in images}
        self.assertEqual(len(by_src), len(manifest))
        for item in manifest:
            with self.subTest(image=item["output"]):
                image = by_src["img/inputs/" + item["output"]]
                self.assertEqual(image["section"], item["section"])
                self.assertIn(f'href="img/inputs/{item["output"]}"', (DOCS / "index.html").read_text())

    def test_fenton_theory_is_stated_with_its_record(self):
        page = self.pages[DOCS / "index.html"]
        home = (DOCS / "index.html").read_text()
        self.assertEqual(page.sections.index("fenton"), page.sections.index("pattern") + 1)
        self.assertIn("https://x.com/GenomicSETI/status/1894160610822426795", home)
        self.assertIn('href="data/fenton-thread.md"', home)
        self.assertIn('src="img/fenton-map.svg"', home)
        self.assertEqual(len(re.findall(r'<article class="claim(?: flip)?"', home)), 13)
        self.assertEqual(home.count('class="note fenton-note"'), 6)
        transcript = (ROOT / "research/fenton/thread.md").read_text()
        self.assertEqual(transcript, (DOCS / "data/fenton-thread.md").read_text())
        self.assertIn("[GAP:", transcript)
        for item in json.loads((ROOT / "research/images.json").read_text()):
            if item["section"] == "fenton":
                self.assertIn(Path(item["output"]).name, transcript)
        for anchor in ("fenton-bird", "fenton-buckets", "fenton-t", "fenton-snakes", "fenton-feathers", "fenton-olmec", "fenton-lore", "fenton-sunda"):
            self.assertIn(anchor, page.ids)

    def test_narrative_bookmark_page_does_not_duplicate_content(self):
        page = self.pages[DOCS / "narrative.html"]
        self.assertEqual(page.images, [])
        self.assertIn("./#narrative", page.links)
        self.assertIn("location.replace(destination.href)", (DOCS / "narrative.html").read_text())

    def test_personal_bylines_are_removed(self):
        for path, page in self.pages.items():
            with self.subTest(page=path.name):
                text = " ".join(page.text)
                # a cited article title ("was Göbekli Tepe built by Aboriginal Australians?") is not a byline
                self.assertNotRegex(text, r"(?i)\b(?:built by(?! aboriginal)|a project by|deep memory, by)\b")

    def test_new_audit_is_not_presented_as_a_completed_redo(self):
        study = next(s for s in self.studies if s["id"] == "civilisers")
        self.assertIn("has not rerun the similarity test", study["finding"])
        self.assertIn("New source-audit pilot", study["versions"][1]["label"])
        draft = (ROOT / "research/civilisers/v3/protocol-draft.md").read_text()
        self.assertIn("Status: proposed, not run", draft)

    def test_unique_html_ids(self):
        for path, page in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual(len(page.ids), len(set(page.ids)))

    def test_local_links_and_anchors(self):
        for path, page in self.pages.items():
            for href in page.links:
                parts = urlsplit(href)
                if parts.scheme or parts.netloc:
                    continue
                target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
                if target.is_dir():
                    target /= "index.html"
                with self.subTest(page=path.name, href=href):
                    self.assertTrue(target.is_file(), f"Missing file: {target}")
                    if parts.fragment and target in self.pages:
                        self.assertIn(unquote(parts.fragment), self.pages[target].ids)

    def test_new_pages_have_image_alternatives(self):
        for name in ("index.html", "narrative.html", "civilisers.html"):
            for image in self.pages[DOCS / name].images:
                self.assertTrue(image.get("alt"), (name, image.get("src")))

    def test_all_passages_are_readable_without_javascript(self):
        page = (DOCS / "civilisers.html").read_text()
        for passage in self.data["passages"]:
            self.assertIn(f'id="{passage["id"]}"', page)
            self.assertIn(publish.esc(passage["paraphrase"]), page)
        self.assertEqual(page.count('class="evidence-card"'), 29)

    def test_publisher_requires_unambiguous_markers(self):
        with self.assertRaises(ValueError):
            publish.replace_region("No markers", "sample", "Content")
        with self.assertRaises(ValueError):
            publish.replace_region("<!-- sample:start --><!-- sample:start --><!-- sample:end -->", "sample", "Content")

    def test_generated_content_is_html_escaped(self):
        data = deepcopy(self.data)
        data["passages"][0]["title"] = '<script>alert("unsafe")</script>'
        rendered = publish.render_evidence(data)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_no_unfilled_generated_regions(self):
        for name in ("index.html", "civilisers.html"):
            page = (DOCS / name).read_text()
            for match in re.finditer(r'<!-- ([\w-]+):start -->([\s\S]*?)<!-- \1:end -->', page):
                self.assertTrue(match[2].strip(), (name, match[1]))


if __name__ == "__main__":
    unittest.main()
