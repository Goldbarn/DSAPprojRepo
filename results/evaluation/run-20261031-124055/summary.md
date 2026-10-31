# Summary: run-20261031-124055

## Headline measurements

- Unmarked false-positive rate: 3/150 = 2.0%
- Detection rate on watermarking outputs: 7/10 = 70.0%
- Usable watermarking success rate: 0/10 = 0.0%; zero-error 95% upper bound 3/n = 30.0%
- Attempts reaching the target: 6/10
- Unmarked source documents: 31

## Unmarked passages by length group

| Group | Flagged | Tested |
| --- | ---: | ---: |
| 30-99 | 2 | 50 |
| 100-199 | 1 | 50 |
| 200-400 | 0 | 50 |

## Watermarking attempts

| ID | Before | After | Flagged | Target | Stop | Changed words | Meaning | Readable |
| --- | ---: | ---: | --- | --- | --- | ---: | --- | --- |
| 2600-1571 | 0.453125 | 0.562500 | True | True | target_reached | 14 | no | no |
| 514-0605 | 0.409524 | 0.561905 | True | True | target_reached | 16 | no | no |
| 2554-0062 | 0.423077 | 0.551181 | True | False | no_more_candidates | 21 | no | no |
| 2600-2189 | 0.364964 | 0.544118 | False | False | no_more_candidates | 25 | yes | no |
| 46-0155 | 0.427273 | 0.568807 | True | True | target_reached | 16 | no | no |
| 1400-0614 | 0.377193 | 0.491071 | False | False | no_more_candidates | 15 | yes | no |
| 84-0017 | 0.442029 | 0.565217 | True | True | target_reached | 17 | yes | no |
| S05-0533 | 0.374101 | 0.566176 | True | True | target_reached | 29 | yes | no |
| 1184-1511 | 0.500000 | 0.543689 | False | False | no_more_candidates | 6 | no | no |
| 345-0233 | 0.497326 | 0.562842 | True | True | target_reached | 16 | yes | no |

## Most repetitive unmarked passage

- S22-0282: 109 distinct / 289 total words, score 0.442907, flagged False
