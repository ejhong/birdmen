# Study 5: the raven and the dove — pre-registration

Written 4 September 2026, before any story was coded. Changes are logged at the end.

## Question
Flood stories are found on every continent. The lost-civilisation literature reads them as a shared memory of one real cataclysm at the end of the Ice Age. The alternative is that floods are universal, that stories about them arise everywhere, and that the specific details which make the world's flood stories look like one story are the details of one story, Genesis, carried by missionaries and traders in the last five centuries. Which details travel with which?

## Corpus
Mark Isaak's *Flood Stories from Around the World* (talkorigins.org/faqs/flood-myths.html): 263 summaries with sources, grouped by region and, on a companion page, by language family. Its limits are recorded: summaries not full texts; the year attached is the compiler's or collector's publication year, not the date the story was told; coverage follows what was published in English.

## Coding
Claude Sonnet 5 reads each summary and answers 26 yes/no/unclear questions (warning by a god; a vessel built; animals taken; birds sent out; raven or dove named; mountain landing; sacrifice after; rainbow or promise; the number forty; earth-diver; repopulation from stones; and so on), plus vessel type and survivor count, from the text only, without naming the culture.

## Analysis (fixed in advance)
1. Prevalence of every detail by region.
2. A *diagnostic* score: the count of seven details specific to the Genesis account and its Mesopotamian ancestors (warning by a god, animals taken, birds sent out, raven or dove, sacrifice after, rainbow or promise, the number forty), as against *generic* details any flood story might have (punishment, a lone survivor, a mountain, the whole world, a vessel).
3. Outside the ancient Near East and classical world (where the Genesis family is documented), the share of stories with three or more diagnostic details, and whether those stories themselves mention Noah, the Bible or missionaries.
4. Jaccard similarity between stories on all details; nearest neighbours of the Hebrew story; within-region versus between-region similarity with a permutation test; the most region-distinctive details.

## Predictions
If the flood stories share one ancient source, the diagnostic details should be spread across regions independent of contact with the Bible, and similarity should not be strongly regional. If they are local stories plus Biblical diffusion, the diagnostic details should concentrate in the Near East and in stories that themselves show Christian contact, and similarity should be strongly regional (earth-diver in North America, sibling repopulation in East Asia, gourds in Africa and Southeast Asia).

## Change log
- 4 Sept 2026, after reading the list of far stories with three or more diagnostic details (post hoc, labelled on the page): the coder's "mentions the Bible, Noah or missionaries" flag missed summaries that name Christ, angels, saints or Noéh, so a keyword flag for Christian names and terms was added to every summary and is reported alongside. The language-family parse of Isaak's companion page was corrected (the first parse had mis-assigned most families). No threshold or prediction changed.
