# Initial data profile

Measured on 2026-09-11 from checksum-verified Help Desk Tickets v3 files. Reproduce with `scripts/profile_data.py`. Detailed evidence: [profile JSON](../reports/initial-profile.json), [column audit](../reports/column-profile.csv), and [initial transitions](../reports/initial-status-transitions.csv).

## Inventory and integrity

| File | Rows | Columns | Grain |
|---|---:|---:|---|
| issues.csv | 66,691 | 58 | One issue |
| issues_change_history.csv | 257,508 | 6 | One field change |
| issues_snapshot.csv | 90,963 | 60 | One issue/assignee cycle |
| sample_utterances.csv | 30,104 | 9 | One utterance |
| holidays_by_country.csv | 4,479 | 2 | Country/date |

All five CSVs have zero exact duplicate rows under string-preserving parsing. Issue and history IDs have zero duplicate keys. History, snapshots and utterances have zero orphan rows relative to issues. Snapshot coverage is 66,691 issues. History covers 66,650, leaving 41 issues without history. These are specific checks, not a claim that the data is clean.

The appraisal workbook has 747 rows on Sheet1. Rows represent appraisal records, not 747 independent tickets or validated AI targets.

## Material findings

1. **Mixed work population.** Type values include Ticket (45,275), Service (5,300), HD Service (1,686), but also Story, Vacation, Project, Epic and others. All 66,691 records must not be presented as IT incidents. No service cohort is approved yet. Type alone may be insufficient to distinguish support from internal work.
2. **Unequal time coverage.** Issue creation spans 2007-04-15 to 2023-03-14. History begins 2015-08-12. This demonstrates incomplete early lifecycle coverage at the export level, although per-case completeness remains to be assessed. The v3 landing page’s 2007 start matches the raw issue range; FEATURES.md still says January 2016. Do not silently drop earlier issues or count unobserved early events as absent.
3. **Long durations need explanation.** 22,414 issues have more than 365 calendar days between creation and recorded resolution. There are no negative or zero resolution intervals among parseable resolved issues; 853 have missing resolution dates. Legacy imports, bulk closure, non-support work, or actual long cases are hypotheses, not established causes. No MTTR claim is approved.
4. **Sparse assignment and priority.** Final assignee is blank in 31,047 issues. Priority is the literal value `unknown` in 33,965. A blank final assignee does not prove the ticket was never assigned. `unknown` is semantically missing even though it is not a blank cell.
5. **Event-order ambiguity.** 164 status rows from 57 issues share a status timestamp with another row in the same issue. Initial transition counting excludes those entire cases and cases with invalid status timestamps. It does not break ties using row position or an assumed ID order.
6. **Limited text coverage.** 30,104 utterances cover 360 issues and 7,286 distinct comment IDs. Twenty-three utterances are blank; 11,497 contain a `ph_` placeholder. Text timestamps span 2022-01-02 to 2023-03-07. Thirty thousand utterances do not constitute thirty thousand independent examples. Sample selection and domain coverage remain to be evaluated.
7. **State-duration sparsity.** Many `wf_` columns are blank. These may encode unvisited states, but converting blanks to zero requires reconciliation with `wfe_` visit counts and publisher extraction logic. Blank, zero and unknown are distinct for now.

All nonblank values in the timestamp columns tested parsed successfully. The column audit records blank counts, distinct values, surrounding whitespace and Unicode replacement characters. It does not prove absence of every possible encoding defect or semantic category mismatch.

## Preliminary process evidence

The transition export counts adjacent observed status updates for 66,536 cases after excluding ambiguous/invalid cases. It retains repeated same-state updates. Frequent observed pairs include resolved → closed (28,271), in_progress → waiting (21,694), waiting → resolved (14,121), and in_progress → resolved (13,910).

These are transition occurrences across the mixed population, not numbers of inefficient incidents. In particular, waiting can be necessary customer coordination. A state update is not necessarily a human touch, and an assignee change is not necessarily an avoidable handoff.

## Before the full profiling milestone can close

- Establish defensible service cohorts by type/project and time coverage; retain exclusion counts.
- Reconcile initial/final states with history, repeated updates, timestamp ties and change groups.
- Check history/comment timestamps against issue creation and resolution; inspect out-of-order source rows without assuming source order is chronological.
- Reconstruct assignee cycles, test composite keys and compare them to publisher snapshots.
- Reconcile derived duration and visit columns with raw events; diagnose the >365-day population by cohort and closure date.
- Audit categorical aliases such as Subtask/Sub-task and missing-value sentinels without automatic merging.
- Verify text/appraisal sample relationships and determine the eligible independent case count for future experiments.
- Register point-in-time availability for all candidate features. Final outcomes, end timestamps, total comments, final assignee, total workflow time and appraisal scores cannot be intake predictors.
- Define censoring and observation-window rules before backlog, reopening or elapsed-time baselines.

No operational problem, causal explanation, AI accuracy, or savings figure is established by this initial profile.
