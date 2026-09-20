# A comparison set for the bird and rounded form

20 September 2026. Selection rules recorded before acquiring the new museum batch.
This is an exploratory, source-bounded comparison set, not a random sample of
ancient art, a worldwide rarity test or a frozen AI experiment.

## Included sources

1. Retain all nine physical objects/surfaces in `../context.json`, including the
   three Göbekli Tepe pillars whose photographs were not previously acquired.
   Missing photographs remain visible as coverage gaps; they are not exclusions.
2. Query the Metropolitan Museum collection API with `title=true`, `hasImages=true`
   and each of `Horus`, `Thoth`, `winged protective spirit`. Retain each search
   response and inspect candidates in ascending numeric object-ID order.
3. For each query, take the first four distinct objects with a public-domain image,
   a non-empty museum title, and a museum end-date at or before 600 CE. A query
   match must concern the depicted subject in the title, rather than a modern
   artist or donor. Skip duplicates of an already selected physical object; retain
   a reason for every exclusion inspected before the quota is reached.
4. End each query at four eligible distinct objects, or exhaustion of its returned
   records. Do not substitute a more striking photograph for a qualifying object.
   If the API is unavailable, record the access failure and a separate explicit
   amendment before using a different retrieval method.

This targets 21 objects: nine focal/local records and twelve museum comparisons.
It deliberately supplies nearby visual alternatives (bird heads, rounded crowns,
held objects, human-headed variants); it does not represent all cultures or all
motifs. Multiple reliefs from one building do not constitute independent cultural
histories. Query ordering and the four-object cap are convenience choices, not a
sample-size justification. Report subgroup coverage, never a global chance rate.

## Observation and dating

Record overall figure form and specific spatial relations separately. A wing,
hand, headdress, ring and held object are not interchangeable features. Missing or
obscured evidence stays unresolved. Attach an observation to a depicted figure or
scene; never combine features on separate figures into one supposed motif bundle.

Use museum/excavation records for identity and date scope. Distinguish production,
later carving, depiction, collection and publication. Dates of photographs bound
when a carving existed, not when it was made. Retain native museum date text.

Image annotations are source-informed editorial observations prepared with AI,
not independently reviewed ground truth. Publish their exact source image,
coordinates, qualifications and differences. No model ranking or historical
significance test may use them as independently certified references.

## What this edition can establish

Which literal correspondences can be inspected; which alternatives change the
comparison; what dates and source histories support each proposed historical step.
It cannot establish transmission from visual resemblance alone. A subsequent
recognition diagnostic needs reviewed references and a separately frozen protocol.

## Retrieval amendment 1 — before the replacement query

The exact `winged protective spirit` query returned one record, a nineteenth-century
British locket (891642). Its numeric date fields are zero; its explicit modern
date excludes it. Zero dates are missing metadata, never a year or evidence of
antiquity. Keep this exclusion and the original response.

Add a replacement `Relief panel` title query, taking the first four public-domain,
illustrated records whose museum culture is Assyrian and whose dates are nonzero
and end by 600 CE, in ascending object-ID order. Include human-headed variants.
This changes the retrieval vocabulary, not the number of comparisons or a score.
The Horus batch retains the first four Isis-and-infant objects; their lack of an
obvious bird-headed subject is not a reason to replace them. Thoth priest shabtis
are excluded because their titles identify a priest, not a depiction of Thoth.

## Previously proposed anchor

Retain Met 32.143.7 (322614), already registered as `apkallu` in the wider
catalogue, alongside the twelve newly selected museum objects. It is a named
comparison anchor, not a result of the new query. This gives 22 physical records.
The four newly sampled Assyrian reliefs can be compared with this eagle-headed
example without discarding their human-headed variants or fragmentary views.
