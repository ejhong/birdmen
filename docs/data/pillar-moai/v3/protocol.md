# Can more evidence improve recognition? · view trial 3.0

Development experiment, fixed before requests. This is a controlled follow-up to
the known failures in pilot 2.0, not a held-out archaeological validation.

## Question and design

For each of three carved surfaces (Pillar 43, Hoa Hakananai’a’s back, and the
Orongo boulder), cross two interventions:

| Factor | Condition 1 | Condition 2 |
| --- | --- | --- |
| Photographs supplied | One photograph | The same photograph plus an alternate view |
| Model reasoning effort | Low | High |

Each combination is run twice: once with photograph A first, once with B first.
The single-image condition sees only that first photograph. The two-image
condition sees both, in the corresponding order. This produces 24 fresh requests
on **three surfaces of three objects**, not 24 independent archaeological cases.
The two orders are different inputs, not repeated identical requests. There are
no additional stochastic repeats within a cell.

The six unaltered photographs and provisional categorical references are copied
by reference from pilot 2.0. Their bytes are frozen again, not revised after seeing
responses. They were selected because earlier performance was of interest, not
sampled at random. No new historical rankings or worldwide rarity estimates.

## What is held constant

Use `gpt-5.5-2026-04-23`, the snapshot actually returned in pilot 2.0. All cells
receive the same prompt, feature definitions, structured-output schema, high image
detail and maximum 6,000 output tokens (including reasoning). High reasoning can
consume more of that allowance; incomplete output remains a failure, not a retry.
No tools, prior conversation, place names, dates, source captions, model answers,
reference labels or cross-cultural comparison are supplied. Famous images can
still be recognised; this is unlabelled, not guaranteed blind.

The task is to describe the **first photograph**. A second photograph, when
present, may clarify its visible features; it must not license adding something
outside the first view. All boxes refer to the first photograph. More photographs
also mean more image tokens: this tests an additional-view package, not the
isolated effect of view diversity at a fixed pixel or token budget. No resizing,
cropping, tracing, rotation, contrast enhancement or generated reconstruction.

Use a shuffled, frozen order (seed 4303). Independent requests run sequentially.
No model fallback, automatic retries, response selection or prompt adjustment.

## Readout decided in advance

For every condition show correct / wrong / uncertain / missing answers against
the provisional references. Keep uncertainty and missing calls in the denominator.
The five features are avian figure, large human face, scorpion, standalone round
motif, and three arch-topped forms in a row. Show every object and input order.

Because many answers are easy negatives, report **primary checks separately**:
avian figures on all three surfaces, the absence of a large frontal face on the
moai back, and the presence of the Pillar 43 scorpion. Each condition has ten
primary checks (five object–feature combinations, two image orders), plus thirty
total feature checks. Also show the six avian checks alone.

Show paired changes in outcome when adding a view, separately at each reasoning
level, and when raising reasoning, separately at each view count. Improvement
means not-correct → correct; deterioration means correct → not-correct. Retain
wrong → uncertain and other changes in the detailed records without treating
them as successful recognition. No statistical significance, population error
rate, best-condition promotion or retrospective pass threshold.

Bounding boxes and descriptions are published for inspection. Matching a label
does not validate the localisation or prove the model understood the carving.
References were assembled by AI from photographs and cited records; independent
review remains `not_reviewed`. Historical ranking stays disabled even at 100%.

## Cost and preservation

At most 24 requests, estimated USD 8 ceiling. Reserve USD 0.30 before each call,
covering 24,000 input tokens at USD 5/million and 6,000 output tokens at USD
30/million. The actual six images are much smaller than this input allowance.
Calculate returned usage at undiscounted standard rates. Failed calls retain
their full reservation because usage may be unknown. Provider billing is final.
The runner records a pending request before network access and refuses to retry
any existing record. Stop on an API error; a resume can run only remaining cells.

Freeze protocol, reference manifest, prompt, schema, both relevant code files,
model settings, order and image SHA-256 hashes before the first request. Preserve
all raw responses and recompute the published result from them. The older run
remains intact. Implementation tests exercise missing answers, paired changes,
budget preservation and the prohibition on converting success into history.

API references checked 19 September 2026:

- https://developers.openai.com/api/docs/models/gpt-5.5
- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/docs/guides/structured-outputs
