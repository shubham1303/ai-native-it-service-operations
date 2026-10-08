# Milestone 3: operational problem discovery

Completed 2026-09-11. Evidence is **observed historical data**, not AI performance, causal impact or measured savings.

## Leading direction for validation

**Long and repeated Waiting intervals are the strongest operational issue to investigate next.** Waiting accounts for 42.0% of the eligible cohort's observed status time. Repeated-wait cases are 7.6% of tickets but contribute 25.2% of waiting time. This pattern persists across time-window and project-exclusion checks.

The data does not yet tell us how much waiting is necessary customer coordination, planned delay, missing information or preventable support delay. We have selected a direction for root-cause validation, not a proven waste category or AI use case.

## Baseline and scope

| Historical measure | Result | Denominator / meaning |
|---|---:|---|
| Primary support-ticket population | 17,263 | External-project Ticket records created from 2019 through the observed March 2023 boundary |
| Recorded resolution date available | 16,788 | Completed-date subset; not every case marked Closed has this field |
| Missing recorded resolution date | 475 | Retained in population; 104 are marked Closed, so missing is not equivalent to operationally open |
| Median recorded-resolution elapsed | 6.09 calendar days | 16,788 with available dates |
| Mean recorded-resolution elapsed | 21.39 calendar days | Same subset; strongly right-skewed |
| 90th percentile | 54.08 calendar days | Same subset |
| 95th percentile | 91.96 calendar days | Same subset |
| Eligible status timelines | 17,132 | Used for waiting, state changes and reopen patterns |
| Eligible assignment timelines | 16,379 | 10,496 have at least one observed named handoff; initial assignment is excluded |
| Eligible for both timeline types | 16,370 | Used when comparing multiple handoffs with status behavior |

Recorded resolution is the source date, not necessarily first service restoration. The observed 2023 period is partial, with 266 of 1,425 primary tickets missing resolution dates. Its lower completed-case median must not be presented as improved performance. [Year-by-year baseline](../reports/milestone3/baseline-by-year.csv).

## Where observed time accumulates

| State | Share of all observed status time |
|---|---:|
| Waiting | 41.96% |
| In progress | 18.04% |
| Validation | 10.92% |
| Pending deployment | 10.32% |
| Resolved | 9.57% |
| Resolved under monitoring | 5.22% |
| Other states, including Closed | 3.97% |

The underlying totals sum calendar time across overlapping tickets. They are **not staff hours, outage days, removable waste or savings potential**. Initial unknown periods are excluded; recorded Closed intervals, including time before reopening, are present in the all-state denominator. [State distribution](../reports/milestone3/state-time-distribution.csv).

## Candidate comparison

Ranks are evidence-based analyst judgments rather than a fabricated precision score. Affected populations overlap and must not be added together.

| Rank | Candidate issue | Scale | Operational significance / counterargument | Direction |
|---|---|---|---|---|
| 1 | Long and repeated Waiting intervals | 4,496 tickets have ≥7 cumulative calendar days Waiting; 1,299 have ≥2 observed Waiting entries; union 4,880 | Largest time category; concentrated recurrence subset; waiting may be necessary | Validate reasons and next-decision ownership first |
| 2 | Validation returning to active work | 672 / 17,132, or 3.9% | Large duration association, but 545 cases occur in 2019–2020; workflow changes may explain decline | Keep as alternative; validate meaning of the return |
| 3 | Extended time recorded as Resolved | 937 / 17,132 have ≥7 calendar days in Resolved | Potential closure/monitoring coordination; state semantics and planned holds may explain it | Investigate only with outcome/closure definitions |
| 4 | Reopening after an observed prior state | 616 / 17,132, or 3.6% | Potential repeated service work, but new requests can reuse tickets | Review intent rather than equating every reopening with failure |
| 5 | Multiple named handoffs | 3,208 / 16,370 joint-eligible cases, or 19.6% | Broad scale, smaller duration association; specialization and first-line transfers may be appropriate | No evidence yet that routing is the main problem |

Seven days is a transparent diagnostic threshold, **not an SLA**. Multiple handoffs means at least two observed changes between different nonblank people; it does not mean group bouncing. Repeated Waiting counts distinct observed entries after collapsing repeated same-value updates. [Full candidate measurements](../reports/milestone3/candidate-observations.csv).

## Why waiting leads

Waiting appears in 10,071 of 17,132 eligible tickets (58.8%). The 1,299 repeated-wait cases represent 22.9% of total observed status time and 25.2% of waiting time. Long-wait cases contribute 91.9% of waiting time, partly by construction because the flag is defined by accumulated waiting. Repeated and long waiting overlap in 915 cases.

Among cases with recorded resolution dates, repeated-wait tickets have a median of **33.93 days**, compared with **5.27 days** for other eligible tickets. The descriptive median gap is **28.67 days**. This is an association, **not** 28.67 days caused by repetition or available to save. Difficult tickets can require both more elapsed time and more waiting; longer observation creates more opportunities for recurrence.

## Robustness and uncertainty

- Waiting time share is 33.9%–49.8% across full creation years 2019–2022. It remains 41.85% when partial 2023 is excluded.
- Removing the single largest waiting-time project leaves 41.33%; removing the ten largest leaves 41.31%. The top ten represent 29.0% of all waiting time, so the aggregate pattern is not solely their contribution.
- Starts from 2016–2020 yield 40.7%–44.2% waiting share for external Ticket records. Broader service types show 42.6%–47.9%. These are sensitivity populations, not pooled extra evidence from independent systems.
- Excluding cases with more than 365 observed days yields 43.96%. This is a diagnostic tail check, not the main cohort rule.
- Clipping time to a selected first-30-day observation check yields 47.50%. The selection rule requires sufficient endpoint exposure or recorded resolution with Closed state within 30 days. This check does not establish complete capture or remove outcome-based selection.
- For the selected 12,163 cases with an observed Resolved entry, Waiting is 56.34% of time before that first entry. Direct-to-Closed cases are excluded from this check. First Resolved is still not verified restoration.
- Excluding Closed/Done/Cancelled time from the denominator yields 43.46% Waiting. Requiring positive-duration Waiting intervals still gives 1,284 repeated-wait cases, compared with 1,299 including zero-duration boundary observations.
- Long-wait case counts are 6,306 at 3 days, 4,496 at 7 days, 2,784 at 14 days and 1,295 at 30 days. The severity threshold changes scale, not the observed existence of substantial waiting. None is an SLA.
- In 66 year × recorded-priority × project strata with at least five completed cases in each comparison group, repeated-wait cases have a higher median in 63. These strata cover only 3,402 completed cases; the result cannot be generalized as full-cohort adjustment.
- The unadjusted repeated-wait median gap's empirical 95% percentile interval is 24.81–32.23 days under case resampling, and 22.05–35.62 under project-cluster resampling. These are exploratory stability checks on the observed sample, not causal intervals or preregistered confirmatory tests.

Source quality exclusions are not random. Of 131 status-ineligible primary cases, 51 lack recorded resolution; among 17,132 included cases, 424 lack it. Assignment exclusion removes 884 cases and its resolved subset has a longer median than included cases. Conclusions therefore apply to the eligible recorded populations, not all company tickets. [Exclusion sensitivity](../reports/milestone3/exclusion-sensitivity.csv).

## What is proven, suggested and unknown

**Observed:** the measured state-time distribution, recurrence counts, duration associations, cohort sensitivity and sample coverage.

**Suggested:** waiting-related coordination is a higher-value investigation target than immediately building a routing model. Validation returns merit investigation but show pronounced time variation.

**Unknown:** why the ticket waited, who could act, whether required information was missing, whether reminders were sent, whether any delay was preventable, whether an alternative process would change outcomes, and whether AI would outperform rules.

The text sample is enriched for difficult paths: 57/340 (16.8%) primary text cases have repeated Waiting versus 325/5,404 (6.0%) among eligible 2022 tickets. Long Waiting occurs in 146/340 (42.9%) sampled cases versus 1,408/5,404 (26.1%) in 2022. Do not infer full-population reason prevalence or future AI performance from this sample without accounting for selection.

**Recommendation:** proceed to the validation plan in [business-problem.md](business-problem.md). No AI intervention, TO-BE workflow or benefit estimate is approved yet.

## Reproduction and artifacts

`python scripts/discover_operations.py` reads the validated database without modifying it. SQL aggregates each child stream to one row per issue before joining. Case grain and independent SQL time sums are checked. The [discovery summary](../reports/milestone3/discovery-summary.json) includes code hashes, seed and method outputs. Eighteen tests passed after adding four discovery contracts to the existing fourteen.

Complete outputs include baseline, candidate comparisons/overlap, project concentrations, time/priority segments, window sensitivity, excluded-record summaries and text-candidate coverage in `reports/milestone3/`.
