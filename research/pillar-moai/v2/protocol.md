# Recognition before resemblance · pilot 2.0

Status: protocol fixed before the new API calls. This is a small, purposively
selected diagnostic, not a preregistered confirmatory archaeology study.
The machine-readable freeze records the protocol, prompt, schema, reference
annotations, image bytes and runner hashes before the first request.

## Question

Can a vision model identify visible carved features without inventing a frontal
face on the back of a moai? Does its reading persist across two photographs of
the same surface and across two independent requests? This diagnostic responds
to errors found retrospectively in the earlier image studies. The targets are
already known to this project; they cannot be called held-out discoveries.

## Materials and reference annotations

Ten photographs, seven object/surface groups: two views of Pillar 43; two views of
Hoa Hakananai'a's back; one view of its front; two photographs of the Orongo
birdman boulder (a modern supplied reference and the 1919 published photograph);
an Orongo relief with three birdmen; Urfa Man; and the Delphi omphalos.

The front and back of Hoa Hakananai'a are separate surfaces of ONE object.
Ten images are not ten independent artefacts. Seven groups include two surfaces of
that object, so the set covers SIX objects/rock surfaces. Two requests per
image give twenty planned responses, not twenty independent historical cases.

Reference observations were assembled by the implementing AI from the cited
object records and visual inspection. They are provisional, not expert ground
truth. Uncertain features have null references and are excluded from scoring.
No species, garment, deity, intended meaning or historical relationship is
scored. Bounding boxes and prose are published for inspection, not automatically
declared correct because a categorical answer matches.

## Input and output

One unaltered JPEG per request, native retained resolution, `detail: high`.
No object name, place, date, file name, paired comparison, explanatory text,
reference answers or historical hypothesis is sent. Famous objects may still
be recognised. This is an unlabelled task, not a guarantee of blindness.

The same five questions are asked of every photograph: avian figure, large
human face, scorpion, a standalone round motif (not an eye), and three arched
forms in a row. First request a short literal description. Each feature gets
present / absent / uncertain, a visual explanation, and an optional bounding
box in normalised image coordinates. Uncertainty is a legitimate response.

Model: `gpt-5.5`, chosen to revisit one model used in the earlier pilots.
Two fresh requests per image; deterministic request order uses seed 4301.
Low reasoning effort, maximum 3,500 output tokens, no tools, no conversation
history, no automatic API retries. Actual returned model identifier and token
usage are saved. One model is not a consensus and this is not a comparison of
old and new prompts under identical conditions.

## Readout fixed in advance

Report every planned request, including failures and incomplete responses.
For non-null references, report correct / wrong / abstained counts; an uncertain
answer counts as abstention and remains in the denominator. Report accuracy
among answered items separately from coverage. Show image-level results,
repeat disagreement and cross-view consistency. Do not calculate significance
from repeated photographs or attach a population confidence interval to this
purposive sample.

Screening threshold: at least 90% of all scorable answers correct, no false
large face on either back view, and no missed avian figure on either back view.
Missing, invalid and uncertain critical answers fail this screening gate.
The numerical threshold is a conservative engineering choice, not an estimated
scientific standard. A pass only permits developing a broader validation set.

**Historical ranking remains disabled regardless of this pilot's score.** It
requires independent human review of the annotations, localisation and captions,
a substantially broader held-out set, and a prespecified comparison corpus.
The reviewer status begins `not_reviewed`; a software result must never promote it.

## Cost and reproducibility

Maximum twenty planned calls and a USD 5 estimated-cost ceiling. Before a call,
reserve USD 0.23 (25,000 input tokens at USD 5/million plus 3,500 output tokens at
USD 30/million). Retained images are below three megapixels. Charged usage is
recorded using undiscounted published rates; failed calls reserve the whole
amount because actual usage may be unknown. API provider billing remains the
authority. No automatic retries or silent model fallback. Re-running resumes
the same frozen run and never replaces responses. If inputs change, start a new
version. Sources for API details and prices, checked 19 September 2026:

- https://developers.openai.com/api/docs/models/gpt-5.5
- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/docs/guides/structured-outputs

## The next experiment, after independent validation

1. Establish object-level identities, image rights and independent local
   reference sets. Have Rapanui and Anatolian specialists review observations.
2. Register similarity features separately from meanings: shapes, depicted
   entities, relations and layout. Analyse the boulder and whole moai as separate
   comparisons. Record correspondence and mismatch before rating resemblance.
3. Choose controls in advance: different photos of the same surface; related
   local designs; documented transmission; bird-plus-round-object examples;
   bird figures without discs; carved stones without bird figures. Match image
   quality and depictive complexity, not only the stone's physical shape.
4. Deduplicate by artefact and site. Reserve held-out objects before prompt
   development. Use equal pixel budgets and randomised order, with original
   and neutral-background conditions applied symmetrically to all images.
5. Compare unaided human judgments and models which pass perception checks.
   Log recognition of origins. Publish failures and inter-rater disagreement.
6. Use object-level uncertainty, stratified baselines and sensitivity analyses.
   A worldwide rarity claim needs a defensible sampling frame. Neither a high
   rank nor a low rank is by itself a test of contact or shared ancestry.

Original studies, raw responses and original preregistrations remain unchanged.
