# Baseline prompt

Run this in a fresh session in the fixture repository, with none of the kit's skills installed or mentioned. Replace the hashes.

```
Review the changes between <base> and <head> in this repository. The domain model is in docs/domain/ and CONTEXT.md. Report every problem you find, with file and line, most serious first.
```

Score the report against `expected-findings.md` exactly as for a reviewer run. The difference between this score and a skill's score is what the skill adds. If the baseline already catches a seed, that seed says nothing about the skill.
