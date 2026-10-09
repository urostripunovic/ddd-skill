# What `tools/check-model.sh` checks

It checks the structure: every template section present (with "None." where empty), state-field types, signatures against the tables, matrix cells, unique example numbers, an example for every command and decision failure, selected glossary names and rejected synonyms, the terms that cross this context's boundaries in the context map, the strict-commands line, that no model section follows the notes tail, and what an approved status may rest on at its depth. It rejects an unconfirmed core, and prints each strict scope.

It does not tell whether a model changed after it was approved or reviewed (`git log -p <file>` does), prove that a state is reachable, check payloads, judge whether a fact's trust rule is enough, cover use-case failures or every glossary term, or judge whether an example follows the rules. A passing check is a starting point, not a verdict; read the rest at the effective depth.
