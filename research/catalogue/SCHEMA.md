# Catalogue schema 2

The default unit of browsing is a **motif family across any number of cultures**.
Specific proposed connections remain attributed comparison claims. They need not
form pairs, and neither family membership nor a drawn connection establishes contact.

| Record | Role |
| --- | --- |
| `families` | A question and a set of literal feature definitions, with links to claims. |
| `attestations` | One evidence entity, a scope (surface, scene, witness, corpus), an explicit subset of features, status, sources and indices of the relevant entity dates. |
| `cultures` | Contextual browsing groups. Their observed date range is not their complete lifespan. |
| `entities` | Objects, carving surfaces, narrative witnesses or labelled corpus records. `physical_id` links views/surfaces of the same physical object. |
| `groups` | Selected examples with a stated membership rationale. |
| `claims` | Who proposes which comparison, its features, differences, transmission assessment and next checks. Any number of groups may participate. |
| `leads` | Unidentified or partially identified supplied material. Links to families, original inputs, images, source checks, panel-level identities and a next step. |
| `media`, `sources` | Image provenance and documentary sources, independent of the claim or motif membership. |

`motifs` remain broad discovery tags on claims/families. They are **not observations**.
“Birds” on a claim does not turn every member into a birdman; a handle on one
object plus a bird on another does not establish the same bundle on either.

An attestation's `features` are recorded within its stated scope. The set may be
smaller than the family's feature vocabulary. Missing features mean **not recorded**,
not absent. `documented` means source-linked editorial observation, not independent
expert certification. `provisional` preserves a disputed or weakly sourced reading.
Both are visible; a bundle query excludes provisional readings by default.

`date_indices` chooses the episode being compared. Do not apply an original statue
date to later carvings, or a composition date to an alleged person's life. Numerical
dates retain source, type and qualification. Unknown values are null, never zero.

A lead's regional caption does not create a culture or map pin. The staff-holder
montage has 21 panel slots, not 21 verified independent artefacts. Two panels of the
new serpent montage point to the **same** `laventa19` entity. Sydney's modern
Gilgamesh is a reception control, not an ancient Australian occurrence.

Families can begin with only leads; verified identities can be added later without
losing the original claim. Keep the lead and its correction after resolving it.
Family searches cover lead descriptions; culture/date filters use the registered
entities, not unverified caption guesses. Including undated records keeps these
leads discoverable. Review/transmission filters apply to comparison browsing.

`input-coverage.json` gives every original file a hash and destination. Additional
views and contextual arguments are captured without inflating the object count.
Validation fails when an input is added or changed without updating its record.

The schema supports growth; the present curated sample does not support worldwide
motif frequency estimates. Broad collection and independent source review remain
ongoing work.
