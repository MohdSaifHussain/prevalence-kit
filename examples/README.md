# Examples

Two, and they exist for different reasons. Read the one that matches what you
are trying to find out.

| | What it is | Read it to |
|---|---|---|
| [`real-data/`](real-data) | A complete measurement on 97,320 real comments with real human labels, checked against a census truth | See the tool do its actual job, and re-run it yourself in about a second |
| [`synthetic/`](synthetic) | 200 fabricated items, 40 sampled, 9 positive by construction | Exercise the machinery — sealing, chunking, tamper detection, refusals — on data that can be published without a second thought |

Both run offline from what is committed here. Neither needs a network
connection, a corpus download, or credentials.

## Start here

```
cd real-data
prevalence-kit plan          plan.yaml            --run run
prevalence-kit sample        plan.yaml frame.txt  --run run
prevalence-kit ingest-labels plan.yaml labels.csv --run run
prevalence-kit estimate      plan.yaml            --run run
prevalence-kit verify        --run run --plan plan.yaml
prevalence-kit emit-report   plan.yaml            --run run
```

`docs/SOP.md` walks through the same six steps slowly, explains what each
artifact is for, and lists what every refusal means and what to do about it.

## Why the synthetic example is not the boring one

It is fabricated on purpose and it is where the guarantees are tested. One of
its 40 items has content spanning four sealing chunks, deliberately, so that a
tamper test can swap two chunks **within a single item** and demand the right
reason code. That property is asserted by the record checker, because it was
lost once already when this directory was created and a fixture regressed —
`docs/CORRECTIONS.md` C-15.

Its true prevalence is 9 of 40 by construction, so a person reading the report
has something to judge the interval against by eye.

## Why the real-data example carries no comment text

`real-data/labels.csv` has item identifiers and label values and no text. This
tool exists to keep harmful content sealed; publishing what it seals would
contradict it. `content` is an optional column and the whole chain runs without
it. The full reasoning is in that example's README and in the decision it came
from, D-54.
