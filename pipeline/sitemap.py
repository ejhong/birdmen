"""One navigation and one site map, shared by every page the site publishes.

The site grew to more than twenty pages across three page shells. These helpers
keep the header links and the footer index identical wherever they appear.
"""
import html

NAV = [('catalogue.html', 'The collection'), ('clusters.html', 'Clusters'),
       ('submerged.html', 'Submerged worlds'), ('research-review.html', 'Research')]

SECTIONS = [
    ('The collection', [
        ('catalogue.html', 'Motif families'),
        ('clusters.html', 'Culture clusters'),
        ('catalogue.html?view=gallery', 'Comparison threads'),
        ('catalogue.html?view=map', 'Map &amp; chronology'),
        ('input-audit.html', 'Input coverage audit'),
    ]),
    ('The central case', [
        ('pillar-and-moai.html', 'The pillar, the moai &amp; the bird'),
        ('fieldwork.html', 'Visual investigation'),
        ('local-context.html', 'Local context'),
        ('atlas.html', 'Illustrated atlas'),
        ('fenton.html', 'A proposed southern route'),
    ]),
    ('Submerged worlds', [
        ('submerged.html', 'The programme'),
        ('bathymetry-lab.html', 'Bathymetry lab'),
        ('research-review.html', 'Findings &amp; next tests'),
        ('signal-audit.html', 'Teaching-figure audit'),
    ]),
    ('The five studies', [
        ('rongo/', 'Indus &amp; rongorongo'),
        ('myths.html', 'Birds, serpents &amp; centres'),
        ('pictures.html', 'The pillar &amp; the moai'),
        ('civilisers.html', 'The civilisers'),
        ('floods.html', 'The raven &amp; the dove'),
        ('recognition.html', 'Recognition trials'),
    ]),
]


def nav(prefix='', current=''):
    return ''.join(
        f'<a href="{prefix}{url}"{" aria-current=\"page\"" if url == current else ""}>{label}</a>'
        for url, label in NAV)


def footer(prefix=''):
    columns = ''.join(
        f'<nav class="footer-column" aria-label="{html.escape(title, quote=True)}"><h2>{title}</h2><ul>'
        + ''.join(f'<li><a href="{prefix}{url}">{label}</a></li>' for url, label in links)
        + '</ul></nav>' for title, links in SECTIONS)
    return f'''<footer class="site-footer">
<div class="footer-inner">
<div class="footer-brand"><a class="footer-mark" href="{prefix or './'}">Deep Memory</a>
<p>An open inquiry into resemblance across distant cultural traditions, and the human landscapes now beneath the sea. Every comparison keeps its source, its date and its unresolved questions.</p></div>
{columns}</div>
<div class="footer-base"><p>A living research notebook · edition September 2026. Inclusion records a question, never an established historical connection.</p>
<p><a href="{prefix}REVISIONS.md">Editorial record</a> · <a href="https://github.com/ejhong/birdmen">Research, code &amp; data</a> · <a href="https://github.com/ejhong/birdmen/issues/new">Corrections and better sources</a></p></div>
</footer>'''
