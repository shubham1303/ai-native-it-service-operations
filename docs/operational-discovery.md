# Where the time goes: the operational baseline

Milestone 3, finished 2026-09-11. Everything here is **observed historical data**. None of it measures AI performance, causal impact or savings.

## What I found

**Long and repeated Waiting intervals are the strongest operational issue to look into next.** Waiting takes up 42.0% of the eligible cohort's observed status time. Tickets that enter Waiting more than once are 7.6% of tickets but contribute 25.2% of waiting time. The pattern holds when I change the time window or leave out the biggest projects.

What the data doesn't tell me yet is how much of that waiting is necessary customer coordination, planned delay, missing information or preventable support delay. I picked a direction for root-cause validation. I haven't proven a waste category or found an AI use case. (Milestone 4 followed this up; see [problem-validation.md](problem-validation.md).)

## Baseline and scope

| Historical measure | Result | Denominator / meaning |
|---|---:|---|
| Primary support-ticket population | 17,263 | External-project Ticket records created from 2019 through the observed March 2023 boundary |
| Recorded resolution date available | 16,788 | Tickets with a completed date; not every ticket marked Closed has one |
| Missing recorded resolution date | 475 | Kept in the population; 104 are marked Closed, so a missing date doesn't mean the ticket is still open |
| Median recorded-resolution elapsed | 6.09 calendar days | The 16,788 with dates |
| Mean recorded-resolution elapsed | 21.39 calendar days | Same subset; strongly right-skewed |
| 90th percentile | 54.08 calendar days | Same subset |
| 95th percentile | 91.96 calendar days | Same subset |
| Eligible status timelines | 17,132 | Used for waiting, state changes and reopen patterns |
| Eligible assignment timelines | 16,379 | 10,496 have at least one observed named handoff; the initial assignment doesn't count |
| Eligible for both timeline types | 16,370 | Used when comparing multiple handoffs with status behavior |

Recorded resolution is the date in the source, not necessarily when service was first restored. 2023 is only partly covered, and 266 of its 1,425 primary tickets have no resolution date. Its lower median for completed tickets shouldn't be read as better performance. [Year-by-year baseline](../reports/milestone3/baseline-by-year.csv).

## Where the time accumulates

| State | Share of all observed status time |
|---|---:|
| Waiting | 41.96% |
| In progress | 18.04% |
| Validation | 10.92% |
| Pending deployment | 10.32% |
| Resolved | 9.57% |
| Resolved under monitoring | 5.22% |
| Other states, including Closed | 3.97% |

These totals add up calendar time across tickets that overlap in time. They are **not staff hours, outage days, removable waste or savings potential**. Initial periods with unknown status are left out. Recorded Closed intervals, including time spent Closed before a reopening, are in the all-state denominator. [State distribution](../reports/milestone3/state-time-distribution.csv).

## The candidates I compared

The ranks are my judgment based on the evidence, not a precision score. The affected groups overlap, so don't add them together.

| Rank | Candidate issue | Scale | Why it matters / the case against | Next step |
|---|---|---|---|---|
| 1 | Long and repeated Waiting intervals | 4,496 tickets have ≥7 cumulative calendar days Waiting; 1,299 have ≥2 observed Waiting entries; union 4,880 | Largest time category; a concentrated subset that keeps coming back; waiting may be necessary | Validate reasons, and who owns the next decision, first |
| 2 | Validation returning to active work | 672 / 17,132, or 3.9% | Strongly associated with duration, but 545 of these tickets are from 2019–2020; workflow changes may explain the decline | Keep as the alternative; check what the return actually means |
| 3 | Extended time recorded as Resolved | 937 / 17,132 have ≥7 calendar days in Resolved | Could be closure or monitoring coordination; what the state means, and planned holds, may explain it | Only investigate once outcome and closure definitions exist |
| 4 | Reopening after an observed prior state | 616 / 17,132, or 3.6% | Could be repeated service work, but new requests can reuse old tickets | Look at intent rather than treating every reopening as a failure |
| 5 | Multiple named handoffs | 3,208 / 16,370 joint-eligible tickets, or 19.6% | Common, but less associated with duration; specialization and first-line transfers can be appropriate | No evidence yet that routing is the main problem |

Seven days is a diagnostic cutoff I chose to be easy to follow. It is **not an SLA**. "Multiple handoffs" means at least two observed changes between different, nonblank people, not a ticket bouncing between groups. Repeated Waiting counts distinct Waiting entries after collapsing repeated updates with the same value. [Full candidate measurements](../reports/milestone3/candidate-observations.csv).

## Why waiting came out on top

Waiting shows up in 10,071 of the 17,132 eligible tickets (58.8%). The 1,299 repeated-wait tickets account for 22.9% of all observed status time and 25.2% of waiting time. Long-wait tickets contribute 91.9% of waiting time, though that's partly by construction, since the flag is defined by accumulated waiting. 915 tickets are both repeated and long.

Among tickets with a recorded resolution date, repeated-wait tickets have a median of **33.93 days**, against **5.27 days** for the other eligible tickets. That's a descriptive gap of **28.67 days** between medians. It's an association. It does **not** mean repetition caused 28.67 days, or that 28.67 days could be saved. Difficult tickets can need both more elapsed time and more waiting, and a ticket that stays open longer has more chances to wait again.

## How robust it is

- Waiting's share of time is 33.9%–49.8% across the full creation years 2019–2022. It's still 41.85% with the partial 2023 left out.
- Removing the single project with the most waiting time leaves 41.33%; removing the top ten leaves 41.31%. The top ten hold 29.0% of all waiting time, so they aren't the whole story.
- External Ticket records starting 2016–2020 give a 40.7%–44.2% waiting share. Broader service types give 42.6%–47.9%. These are sensitivity populations, not extra evidence from independent systems.
- Leaving out tickets with more than 365 observed days gives 43.96%. That's a check on the tail, not the main cohort rule.
- Clipping time to a selected first-30-day window gives 47.50%. The selection requires enough exposure before the end of the data, or a recorded resolution with Closed status within 30 days. This check doesn't show that the data is complete, and it doesn't remove selection based on outcomes.
- For the 12,163 selected tickets with an observed Resolved entry, Waiting is 56.34% of the time before that first entry. Tickets that went straight to Closed are left out of this check, and first Resolved still isn't verified restoration.
- Taking Closed/Done/Cancelled time out of the denominator gives 43.46% Waiting. Requiring Waiting intervals to have positive duration still leaves 1,284 repeated-wait tickets, against 1,299 when zero-duration boundaries are included.
- Long-wait ticket counts are 6,306 at 3 days, 4,496 at 7 days, 2,784 at 14 days and 1,295 at 30 days. The cutoff changes the scale, not the fact that a lot of waiting exists. None of these cutoffs is an SLA.
- In 66 year × recorded-priority × project strata with at least five completed tickets in each comparison group, repeated-wait tickets have a higher median in 63. Those strata only cover 3,402 completed tickets, so this can't stand in for adjusting the full cohort.
- Resampling tickets gives an empirical 95% percentile interval of 24.81–32.23 days for the unadjusted gap between medians, and resampling by project cluster gives 22.05–35.62. These are exploratory stability checks on the observed sample, not causal intervals or preregistered confirmatory tests.

The tickets excluded for data quality aren't excluded at random. Of the 131 status-ineligible primary tickets, 51 lack a recorded resolution; among the 17,132 included, 424 lack one. The assignment rules exclude 884 tickets, and the resolved ones among them have a longer median than the included tickets. So the conclusions apply to the eligible recorded populations, not to every ticket the company had. [Exclusion sensitivity](../reports/milestone3/exclusion-sensitivity.csv).

## What's shown, what's suggested, what's unknown

**Observed:** the distribution of time across states, the recurrence counts, the duration associations, the cohort sensitivity checks and the sample coverage.

**Suggested:** coordination around waiting is a more valuable thing to investigate than jumping straight to a routing model. Validation returns are worth investigating too, but they vary a lot over time.

**Unknown:** why a ticket waited, who could have acted, whether needed information was missing, whether reminders went out, whether any delay was preventable, whether a different process would change outcomes, and whether AI would do better than rules.

The text sample leans toward difficult tickets. 57 of the 340 primary text tickets (16.8%) have repeated Waiting, against 325 of 5,404 (6.0%) among eligible 2022 tickets. Long Waiting appears in 146 of the 340 (42.9%), against 1,408 of 5,404 (26.1%) in 2022. So neither how often each reason occurs in the full population nor how well AI would do later can be read off this sample without accounting for that selection.

**Recommendation:** move on to the validation plan in [business-problem.md](business-problem.md). No AI intervention, TO-BE workflow or benefit estimate is approved yet.

## Reproducing this

`python scripts/discover_operations.py` reads the validated database without changing it. The SQL reduces each child stream to one row per issue before joining. Ticket grain and independent SQL time sums are both checked. The [discovery summary](../reports/milestone3/discovery-summary.json) includes code hashes, the seed and the method outputs. Eighteen tests passed after I added four discovery tests to the existing fourteen.

All the outputs are in `reports/milestone3/`: baseline, candidate comparisons and overlap, project concentrations, time and priority segments, window sensitivity, summaries of excluded records, and text-candidate coverage.
