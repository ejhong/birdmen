# Do Easter Island and the Indus Valley share a script? We ran the test nobody had run.

*Twenty-four look-alike signs have circulated for ninety years. We digitised both complete sign inventories plus twenty-two unrelated scripts, measured them all the same way, and published every step. The resemblance turns out to be ordinary, and the most interesting thing we found was the reason it ever looked special.*

![The circulating chart of 24 Indus and Easter Island sign pairs](https://ejhong.github.io/rongo/img/fig/chart.jpg)

Earlier this month an old idea resurfaced on my feed: a chart of twenty-four pairs of signs, Indus Valley seal signs above, Easter Island rongorongo glyphs below, looking uncannily alike. The account posting it argued that dismissing this as coincidence is like finding the whole English alphabet in another language. A historian replied that each script has 400 to 600 signs, so two dozen look-alikes is "4.8% similarity", and anyway the drawings were made by hand by someone trying to highlight resemblances.

Both are half right. Two inventories of that size offer a quarter of a million candidate pairings, and a motivated eye will find two dozen look-alikes in any two pictographic systems. But dividing 24 by 500 is not a test either. The only honest question is narrower: **are the Indus and rongorongo inventories more alike than two unrelated scripts are, when every script gets exactly the same chance?**

In ninety years of argument, nobody had run that test. The sign lists exist, in scans anyone can download. So we ran it, in the open. The full write-up, with every chart interactive and every number traceable to code, is at **[ejhong.github.io/rongo](https://ejhong.github.io/rongo/)**. This is the short version.

## What we compared

Two target inventories and twenty-two controls.

The targets come from the standard scholarly catalogues: Iravatham Mahadevan's 1977 list of 417 Indus signs, and Thomas Barthel's 1958 plates of rongorongo glyphs, the numbered drawings every later study cites. Both are scans. Code cut out every sign, read its catalogue number from the page, and we checked the results by eye on contact sheets. 417 Indus signs and 604 rongorongo glyphs came out the other end.

![Barthel's plate 6 with the extractor's decisions overlaid](https://ejhong.github.io/rongo/img/fig/barthel_overlay6.jpg)

The controls are the sign inventories of twenty-two other scripts, rendered from Google's Noto fonts: Egyptian hieroglyphs, Anatolian hieroglyphs, cuneiform, Linear A, Linear B, Vai, Nüshu, the Yi syllabary, and fourteen more, spanning five thousand years and four continents. Two of them, Linear A and Linear B, are known to be related. So are several of the small alphabets. Those are the positive controls: a method that cannot see them has no business judging the Indus pair.

## How every sign was measured

The three sources are drawn differently. Barthel's glyphs are hollow outlines, Mahadevan's are thin line drawings, fonts are filled shapes. Compared directly, you would mostly be measuring drawing style. So every sign, from every script, is first reduced to the same thing: its skeleton, a one-pixel stick version of the shape.

![Raw signs beside their skeletons](https://ejhong.github.io/rongo/img/fig/norm_check.png)

Three independent similarity measures are then computed between skeletons and averaged: a pure geometric distance, a classic gradient descriptor, and a frozen general-purpose vision model. The combination was calibrated on random pairs across all scripts before the Indus pair was ever examined. No language model looks at any pair.

Does the method see relatedness at all? Yes. Linear B was adapted from Linear A around 1450 BCE, and their best matches are, to the eye, the same signs. Their score is the highest of all fifty-five script pairs.

![The 24 best one-to-one matches between Linear A and Linear B](https://ejhong.github.io/rongo/img/fig/top_lineara_linearb.png)

## Result 1: middle of the pack

Eleven scripts are large enough to compare fairly. That gives fifty-five script pairs, all scored identically. The main statistic is the "best-24 score": the average similarity of the 24 best one-to-one matches, chosen the way a chart-maker chooses them, with both inventories subsampled to the same size.

![Best-24 score for every pair of the eleven large scripts](https://ejhong.github.io/rongo/img/article/dotplot.png)

Indus–rongorongo ranks 25th of 55. Linear A–Linear B ranks first, far to the right.

But there was a wrinkle, and it is worth dwelling on because it is where the story gets interesting.

![Best-24 from each target's point of view](https://ejhong.github.io/rongo/img/article/vs_bars.png)

Look only at rongorongo's partners and Indus comes first on nearly every statistic. Look only at Indus's partners and rongorongo comes near the bottom. In a lineup test, where each of the 604 rongorongo glyphs is asked which script holds its nearest neighbour, Indus won 41% of the time. Chance is 10%.

## Result 2: it was the handwriting

There is a mundane explanation for that asymmetry. The Indus and rongorongo inventories are the only two that are scanned hand drawings. Every control is a crisp font. If "looks hand-drawn" leaks through skeletonisation into the measures, Indus would be rongorongo's best match for a reason that has nothing to do with the signs.

So we tested it. Every font glyph was passed through a random elastic distortion and a scanner-like blur before entering the pipeline, one fixed setting for all scripts, no tuning. The result looks like a hand copy of the printed sign.

![Font glyphs before and after wobble](https://ejhong.github.io/rongo/img/fig/wobble_check.png)

Then everything was rerun.

![The lineup test with clean and with wobbled controls](https://ejhong.github.io/rongo/img/article/lineup.png)

Indus's share of the lineup fell from 41% to 14%, level with Egyptian and Anatolian and below cuneiform. On the best-24 score, wobbled Egyptian now edges Indus as rongorongo's closest partner, and the ordering among the rest is noise.

![Best-24 with wobbled controls](https://ejhong.github.io/rongo/img/article/vs_bars_wob.png)

Almost all of Indus's apparent edge was the shared texture of hand-drawn scans. This is the kind of artefact that a chart of twenty-four drawings can never reveal and a full-inventory comparison exposes immediately.

## Result 3: every script gets its own chart

The circulating chart is a "best 24" for one pair of scripts, picked by a person. On the site, every pair of large scripts gets its own best 24, picked by the same algorithm from the full inventories, drawn in the same style, with the labels hidden until you click. Here are three of them, revealed.

![Three best-24 panels from the blind tournament](https://ejhong.github.io/rongo/img/article/tournament.png)

Cuneiform against the Yi syllabary, rongorongo against a hand-drawn-style Mende Kikakui, Vai against Yi: none of these scripts has anything to do with the others, and every one of them yields a panel of bars, figure-eights, ovals and forks about as convincing as the bottom row of the famous chart. Vai and Yi, two syllabaries invented on different continents, score higher than Indus and rongorongo do. Only the genuinely related pair, Linear A and Linear B, looks different in kind. Go and play it blind on the site; it is harder than you think.

## Result 4: the twenty-four pairs themselves

Finally, the chart. Each of its 48 drawings was cut out, run through the same pipeline, and matched to the catalogue sign it depicts, with a reviewer's identification recorded and the runners-up kept so anyone can disagree. Then two numbers per pair: how similar the two *drawings* are to each other, and how similar the two *catalogue signs* they stand for are, ranked among all 251,868 Indus–rongorongo pairs.

![Four of the audited chart pairs](https://ejhong.github.io/rongo/img/article/cards.png)

- In 17 of 24 pairs, the drawings on the chart resemble each other more than the catalogue signs do. The redrawing added about half a standard deviation of similarity.
- Only one catalogue pair clears the match threshold: the figure-eight. It is also the single most similar pair of the whole cross-product, and the only mutual nearest neighbour.
- The catalogue pairs sit at the 87th percentile on average. Good look-alikes, but the tail of a quarter-million pairs is a crowded place: thirteen pairs in the whole cross-product clear the threshold, and one of them is on the chart.

![All 251,868 Indus–rongorongo catalogue pairs by similarity](https://ejhong.github.io/rongo/img/article/histogram.png)

The bottom row of the chart, the "nearly identical" simple shapes, is where the real matches are: the figure-eight, the oval with a stroke, the crescent, the lollipop, the fir tree. Those are also the signs with the least design space, the ones every pictographic system contains. The anthropomorphic rows, which would carry real weight if they matched as families, mostly resolve to ordinary Indus stick figures and ordinary rongorongo figures, alike at the level of "a person with something at the right hand" and not much beyond.

## Result 5: the known relatives cluster where they should

The small alphabets have documented family trees. Scoring all 276 pairs of all 24 scripts at the size of the smallest inventory puts them on the same axis as the Indus pair. The relatives cluster at the top. The Indus pair sits at rank 119.

![All 276 pairs of the 24 scripts, with documented relatives marked](https://ejhong.github.io/rongo/img/article/small_panel.png)

## What this does and does not show

It is a catalogue-level test: Barthel's and Mahadevan's drawings, not photographs of tablets and seals. That is a large step up from an advocate's chart, and it is the level at which the claim has always been argued, but a photo-level version is the obvious next step. The controls are fonts, and the wobble experiment shows how much that matters. Sign counting is contested on both sides. And shape similarity, however carefully measured, can never establish or exclude historical contact on its own.

What it can do is answer the narrow, falsifiable question the chart poses: whether these two inventories resemble each other more than unrelated inventories do, under a method that demonstrably detects real relatedness. They do not.

What would change the verdict is spelled out on the site: an Indus–rongorongo score in the top few pairs after wobbled controls, an excess of reciprocal high-complexity matches, or a mapping of sign families that survives permutation. None appeared. The code, the scans, the crops, the QA sheets and every statistic are in the repository for anyone who thinks a different, pre-specified measure would find them.

**Full results, interactive charts, and the blind tournament: [ejhong.github.io/rongo](https://ejhong.github.io/rongo/)**
**Code and data: [github.com/ejhong/rongo](https://github.com/ejhong/rongo)**

*This is the first case study of a test bench for claims of long-distance sign transmission. Corrections and better controls are welcome.*
