# Supported metrics and observation rules

Status: approved definitions for Milestone 3 discovery, not final selected-problem baselines. All measures describe historical records. No metric below measures post-intervention impact.

## Observation boundaries

The latest observed export timestamp is **2023-03-14 14:19:32 UTC**. This is an observed data boundary, not a independently documented extraction contract. An issue's `ended` is the endpoint supplied in its summary. Intervals stop there; we do not assume activity persisted to the global boundary.

The primary population is external-project Ticket records created from 2019-01-01 to the observed export boundary. At extraction, **475** primary cases lack a recorded resolution date. Keep these in volume and missing-outcome counts. Completed-only elapsed-time summaries exclude them and must state their denominator and selection limitation. Treat them as unresolved/unknown outcome at the observed endpoint; do not silently impute a duration.

The source has incomplete initial history and uncertain capture beyond some case endpoints. Thus full-population survival estimates, exact organization backlog and continuous open-state occupancy are not approved yet. If later survival analysis is proposed, establish a justified censoring time separately. Compare equivalent follow-up windows; do not interpret short 2023 durations as improvement.

## Definitions

| Metric | Numerator / calculation | Eligible denominator or scope | Interpretation and restrictions |
|---|---|---|---|
| Ticket volume | Count unique issue IDs by creation period | 17,263 primary records; show partial periods | Recorded support tickets, not all incidents or all company demand |
| Recorded-resolution elapsed | `issue_resolution_date - issue_created`, seconds converted to calendar hours/days | Nonmissing valid recorded resolution among primary records; 16,788 currently | Endpoint-label measure; report median, mean, p90 and eligible count; not labor time or first restored service |
| First observed Resolved entry elapsed | Earliest observed `status=resolved` time minus creation | Eligible status cases with that entry | First **observed** occurrence only; initial history gap disclosed |
| Observed status transitions | Count changes from previous observed value to a different value | 17,132 status-eligible cases | Excludes repeated updates; report transitions and distinct affected tickets separately |
| Waiting occupancy | Sum elapsed seconds in observed Waiting intervals | 17,132 status-eligible cases; zeros when no observed Waiting interval | Time within recorded portion only; cannot call all waiting waste |
| State-entry rate | Distinct eligible cases with an observed entry into state / eligible cases | Explicit status cohort | A label occurrence is not proof of an operational action or human touch |
| Observed reopen-entry rate | Cases with transition from a different observed state into Reopened / status-eligible cases | 17,132; inspect predecessor distribution | Does not count rejected resolutions without that recorded label |
| Observed named handoffs | Changes between two different nonblank assignee IDs | 16,379 assignment-eligible cases | First assignment excluded; group transfers unsupported |
| Cases with a named handoff | Cases with ≥1 named handoff / assignment-eligible cases | 16,379 | Not a full organization transfer rate; missing-history cases are excluded |
| Assignment blank transitions | Changes to/from blank owner, separately counted | Assignment-eligible cases | Cannot interpret blank as a known unassigned state without qualification |
| Data-quality exclusion rate | Primary cases failing the relevant metric gate / primary records | Status: 131/17,263; assignment: 884/17,263 | Separate coverage rates; do not combine or hide exclusions |
| Priority distribution | Count/share of recorded priority labels, including unknown | Explicit cohort and period | Descriptive latest metadata; initial priority not established |

Percentages must use case counts, not event or utterance counts. Aggregate a case once before joining multiple child tables. Duration percentages use summed elapsed time for a stated interval population and must not be presented as staff workload shares.

## Not supported

SLA compliance (no contractual targets), first-contact resolution, true human touches, employee utilization, cost per ticket, hours saved, avoidable handoffs, confirmed escalation, real support capacity, root-cause prevalence and successful technical remediation. These need additional evidence, labels or explicit later simulation assumptions.

## Consumer tables

- `analysis_status_intervals` and `status_transitions`: eligible status observations.
- `analysis_assignment_intervals`: eligible assignment observations.
- `analysis_case_measures`: metric eligibility flags; ineligible metric values are NULL. A valid observed zero is distinct from NULL.
- `case_observed_measures`, `issue_quality`, `observed_intervals`: diagnostic tables retaining broader records; use consumer views for findings.

Raw publisher `wf_*`, `wfe_*`, total comments, final assignee and final status are retrospective data, not automatically safe prediction features.
