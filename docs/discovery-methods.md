# Discovery methods and limitations

## Source and grain

The validated local database comes from the pinned Help Desk Tickets v3 files. `sql/discovery_cases.sql` aggregates status intervals and transitions independently to issue grain, then joins each aggregate once. This prevents the multiplication of state durations by assignment events or utterances. No primary field or eligibility rule is changed by discovery.

The main process population is 17,132 eligible status cases; handoff/time comparisons require 16,370 cases eligible for both histories. Handoff-only counts use 16,379. Recorded-resolution summaries use the defined primary date population. Every report gives its denominator or links to its definition.

## Candidate definitions

- Any Waiting: at least one observed Waiting interval, including a zero-duration boundary observation.
- Repeated Waiting: at least two distinct observed entries; consecutive same-value updates were removed earlier.
- Long Waiting: at least seven cumulative calendar days in Waiting, with 3/14/30-day threshold sensitivity reported. Not a contractual SLA.
- Validation return: observed Validation → In progress change.
- Reopened: entry into Reopened with an observed predecessor.
- Multiple handoffs: at least two changes between different known nonblank assignees.
- Extended Resolved: at least seven cumulative days recorded in Resolved.

Labels describe recorded behavior, not failure causes. Duration-based flags partly define the duration outcome; do not use their associations as causal evidence. All candidate populations overlap.

## Comparisons and uncertainty

Elapsed-resolution associations exclude missing dates from both groups and retain group-specific eligible counts. Unresolved or missing-date cases remain in population and coverage tables. The entire sample is retrospective, with nonrandom missingness, and we do not claim unbiased completion-time estimates.

Exploratory median differences use 1,000 independent case-bootstrap draws with seed 20260911. A second check resamples whole masked projects 500 times with replacement, preserving dependence within each selected project. Percentile intervals use the 2.5th and 97.5th percentiles. Project-level resampling does not resolve dependence across projects, source selection or confounding.

Within-stratum comparisons use year, recorded priority and masked project, requiring at least five completed cases per exposure group. We report the number of strata, overlap cases and direction of median differences. A weighted log-mean difference in `log(1 + calendar days)` is supplied in diagnostic JSON, weighted by the smaller exposure group. It is a descriptive transformed-scale contrast, not a percentage improvement or causal effect. Coverage restrictions matter; only a subset of cases enters these comparisons.

We do not report significance tests, cherry-picked p-values or a causal model. Several candidates are explored, so these are hypothesis-generating comparisons. Severity and complexity may drive both more process steps and longer times; duration also creates more opportunities for repeated events. Recorded priority may differ from initial priority.

## Robustness

Reports vary creation-year start, broad service scope, project concentration, exclusion of partial 2023, long-duration tails and a selected fixed 30-day window. A separate selected subset clips time at first observed Resolved entry. These do not supply unobserved history or establish clinical/technical restoration.

The primary cohort does not filter on favorable outcomes. Tail exclusion is sensitivity only. Source-quality exclusions are reported separately and remain in diagnostic tables. Chronological differences must consider changing follow-up time and missing outcome rates.

## Reproduction

Run `python scripts/discover_operations.py` after the Milestone 2 build. It requires pandas and NumPy only; no model API or paid service. Outputs and code hashes are under `reports/milestone3/`. Run `python -m unittest discover -s tests -v` for source-grain and metric contracts.

The source database stays read-only. No train/test model split or prospective feature dataset is created. Future model evaluation must enforce issue-level separation and outcome availability at the training cutoff, independent of this descriptive discovery.
