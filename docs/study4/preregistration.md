# Study 4: blind lineups of de-identified culture-hero myths — pre-registration

Written 4 September 2026, before any lineup was judged. Changes are logged at the end.

## Question
Are the "civiliser" myths that the lost-civilisation literature groups together (Viracocha, Quetzalcoatl, Kukulkan, Bochica, Votan, Oannes, Osiris, Thoth, Nommo) more alike, as stories, than culture-hero myths from unrelated traditions ordinarily are? And how alike are stories known to share a source?

## Corpus
About 105 myths, each the narrative of one English Wikipedia article (title, URL and revision id recorded): the civiliser set above; documented transmissions used as positive controls (the Gilgamesh flood and the Genesis flood; Atra-Hasis and Gilgamesh; Utnapishtim and Noah; the Ramayana and the Khmer Reamker and Thai Ramakien; the life of the Buddha and Barlaam and Josaphat; the Panchatantra and Kalila wa-Dimna; Manu and Matsya; Deucalion and Noah); same-region pairs related by contact (Quetzalcoatl and Kukulkan; Viracocha and Manco Cápac; Viracocha and Tunupa; Osiris and Isis; Enki and Oannes; Fuxi and Nüwa; the Māori and Hawaiian Māui; Idris and Enoch); and a world pool of culture heroes from every inhabited continent as decoys. Wikipedia is used because it is uniform, cited and reproducible; it is a secondary source and that is a limit.

## Blinding
Claude Sonnet 5 retells each article's myth in 200–300 words using only the article, then rewrites it with every personal, divine, place, people and language-specific name replaced by a role description. The judges see only the de-identified text. A leak test asks Claude Opus 5 to guess the region and figure from each blind text; the share guessed correctly is reported. A judge that recognises a story is not blind, and the result is qualified accordingly.

## Lineups
One target story and ten candidates; one candidate planted; nine decoys drawn at random from the pool, excluding the regions of both target and planted. The judge ranks all ten. Each pair is run in both directions, ten decoy draws each (20 lineups per pair per judge). Sets: `hancock` (11 pairs), `positive` (9 pairs), `related` (8 pairs), `random` (60 lineups, random target and random planted story from another region: the base rate). Judges: Claude Opus 5 and Claude Sonnet 5 (the OpenAI, Gemini and xAI accounts were out of credit when this was written).

## Outcome measures
Rank of the planted story (chance mean 5.5; rank 1 by chance 10%), share ranked first, one-sided binomial p against 0.1. Reported per set, per pair and per judge.

## Predictions
Positive controls are picked out first in most lineups (above 60%). Random pairs near 10%. Same-region pairs between the two. The civiliser pairs are the question: if they are picked out as often as the positive controls, the stories are as alike as stories with a known common source, and that would count for the claim; if they sit near the random base rate, they do not. Any pair is reported individually because the set is heterogeneous.

## Change log
- 4 Sept 2026, after the leak test and before any lineup result was analysed: Claude Opus 5 named the region of 96 of 103 de-identified stories, 96 of them with high confidence, and named Viracocha, Quetzalcoatl, Oannes and Osiris outright. The lineups therefore measure the model's judgment of stories it recognises, not a blind reading, and the page says so. Two knowledge-free instruments were added (post hoc, before any lineup result was read): cosine similarity of the de-identified texts under a local sentence-embedding model (all-MiniLM-L6-v2) and TF-IDF, reporting for every pair the rank of the partner among all stories in the corpus, with the same four sets for calibration. Two articles (Sumé, Amalivaca) had no English Wikipedia page and were dropped; "Oannes" resolves to the Apkallu article, so the corpus holds that article under two keys and same-article neighbours are excluded from the nearest-neighbour lists.
- 4–5 Sept 2026, end of the run: Claude Opus 5 completed all 620 lineups. Claude Sonnet 5 returned a malformed ranking (not a permutation of 1–10, or truncated JSON) in a share of trials even after three attempts and a larger output limit; failed trials were discarded, not counted, and its coverage is 177 of 220 civiliser lineups, 179 of 180 positive controls, 150 of 160 related, 51 of 60 random. Its counts are shown in every table.
