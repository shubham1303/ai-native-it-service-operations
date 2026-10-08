# Milestone 2: validated data and process understanding

Completed 2026-09-11 for a bounded discovery scope. This milestone establishes usable populations, timeline definitions and measurement controls. It does not identify the final business problem or justify an AI intervention.

## Decision

Use **external-project records labeled Ticket, created from 2019-01-01 onward**, as the primary population for discovery. There are **17,263** such records. There are **17,132** with eligible observed status timelines and **16,379** with eligible assignment timelines. These are different metric denominators, not interchangeable sample sizes.

The cohort represents recorded customer software-support work. A ticket can also contain an administrative request or file exchange; neither its label nor our sample review proves it is an IT incident. Use “support tickets” in the portfolio until a narrower incident definition is substantiated.

## Why this population

- The publisher's masking documentation identifies an external-project country prefix C00–C17. We use `^C(?:0[0-9]|1[0-7]).{3,}$` and retain the original code. The prefix is a publisher-based classification rule, not a verified customer master-data relationship.
- The export has 42,803 external-project Ticket records across all years. A broader external Ticket/Service/HD Service population contains 49,725. Non-ticket types remain in staging; they are not silently deleted or renamed.
- On 2018-08-09 and 2018-08-14, 18,509 resolutions were recorded; **18,454** of these records have lifetimes longer than 365 days. This is evidence of a concentrated recording pattern. It is not proof of a migration, bulk-close policy or staff failure.
- The primary window starts with the first full calendar year after those concentrations. This is an analysis choice, not a claim that all later records are complete or that older records are invalid. Alternative starts and broader types are retained in [cohort sensitivity](../reports/milestone2/cohort-sensitivity.csv). Later discovery must check whether conclusions depend on this choice.
- Inclusion does not depend on a ticket being resolved, having a particular priority, or having a short duration. Long-duration and unresolved records remain in the primary population. The 2023 period is partial.

## Reproducible inclusion and exclusion

| Sequential status-cohort step | Remaining records |
|---|---:|
| All exported issues | 66,691 |
| External-project Ticket | 42,803 |
| Created from 2019-01-01 | 17,263 |
| Has status history | 17,238 |
| No conflicting status values at one timestamp | 17,233 |
| Valid event timestamps, none before creation | 17,233 |
| No events after source endpoint | 17,135 |
| Valid issue bounds and matching latest status | 17,132 |

These sequential exclusions differ from overlapping defect counts. For example, 103 primary tickets have events after their source endpoint, but only 98 are removed at that step because earlier filters already removed the others. The [case-quality register](../reports/milestone2/case-quality-register.csv) preserves every issue, its flags and source row. Assignment eligibility independently requires assignment history, unambiguous assignee ordering and valid timeline bounds.

## Quality findings and treatment

| Finding | Measured evidence | Treatment |
|---|---|---|
| Source integrity | Eight source files match publisher SHA-256 hashes | Recheck before each build; retain original bytes |
| Unique keys and relationships | Issue/history keys unique; initial cross-file joins have no orphans | Normalize numeric identifiers using exact decimal conversion; preserve raw keys |
| Source row order | 84 backwards timestamp steps within issue/field source sequences | Sort by parsed timestamp; source row remains lineage only |
| Equivalent repeated observations | 85 duplicate issue/field/time/value observations | Collapse equivalent observations, retain contributing event IDs and multiplicity |
| Conflicting simultaneous values | 9 status-affected issues and 1 assignee-affected issue across all data | Quarantine the affected field's entire case sequence; never guess event order |
| Change-group consistency | No groups span multiple issues or timestamps | Keep group IDs as context; do not use them to invent order within an instant |
| Event boundaries | 1 issue has a pre-creation event; 984 have post-endpoint events | Retain diagnostics; exclude affected cases from approved process measures |
| Latest status | 3 cases disagree with unambiguous latest observed status | Exclude from status cohort |
| Derived negative times | 55 issues have at least one negative publisher state duration; none in primary population | Do not use publisher duration columns as authoritative analytical measures |
| Source time totals | State sums reconcile for 66,613 cases; 78 have all state durations blank | Preserve blanks; structural-zero interpretation only with zero visit count |
| Definition mismatch | Publisher total matches endpoint elapsed time in 66,319 cases, recorded resolution elapsed in 53,945 | Keep endpoint and resolution measures separate |
| State entry vs resolution date | 6,875 primary cases have first Resolved entry and recorded resolution more than 60 seconds apart | No interchangeable “MTTR” label |

No nonblank timestamps failed parsing in the profiled timestamp columns. All numeric state-duration fields and their matching count fields were audited. For every state, blank time coincides with zero publisher visits; there are no blank-time/positive-visit or numeric-time/zero-visit pairs. Raw values remain unchanged. `unknown` priority remains explicit missing information, not a new priority tier. Subtask/Sub-task and other type labels are not merged because equivalence is unproven.

## Timeline reconstruction and reconciliation

The first observed update gives the new value from that instant onward. The period between creation and that update stays unobserved. Every one of the 17,233 primary cases with unambiguous status observations has a positive initial gap; the median is 108 seconds. We do not assume the initial state was Open or extrapolate the first assignee backwards.

Equivalent same-value/time records are merged. Subsequent same-value updates are retained in diagnostics but do not count as new state entries or handoffs. A real value change starts an interval that ends at the next change or source `ended`, whichever occurs first. Negative intervals are prohibited. The last observed state may have a zero-length interval. Cross-field simultaneous status and assignee changes are not ordering conflicts within either field.

Within the eligible primary status cohort, reconstructed durations reconcile within one second for all **14,902** cases with observed In progress intervals, **10,071** with Waiting intervals and **12,163** with Resolved intervals. These reconciliation denominators include zero-length observations. Initial Open time is not independently recoverable. Four eligible cases have a Closed-duration discrepancy, so publisher Closed-duration comparisons are not accepted as a correctness benchmark. The independent event-time calculation is retained and its source boundaries are explicit.

The publisher's workflow counts are not automatically counts of business state transitions. Its worked example divides one In progress stay across two assignment cycles and counts two intervals. Our state-entry and assignment-transition measures therefore come directly from value changes, not `processing_steps` or `wfe_*`.

## Assignment summaries

All 66,691 cases have snapshots whose outer boundaries match issue creation and endpoint. There are no duplicate issue/turn keys, overlapping cycles or gaps; 326 snapshot intervals have zero duration. Of 24,272 later cycles, 24,113 exactly match observed assignee/start/end boundaries. The unmatched cycles remain diagnostic and are not used to repair history.

For 37,389 cases, the first snapshot owner is also the first observed assignee but the snapshot starts earlier than that assignee observation. This demonstrates backward attribution in the summary, not observed initial ownership. We count only changes between two known, different named assignees. Transitions into/out of blank assignment are reported separately. Neither ownership time nor handoff count establishes employee effort or avoidability.

## Exit-gate assessment

**Passed for scoped discovery:** source integrity, reproducible cohort membership, explicit timestamp/endpoint semantics, reconciled main state-duration measures, quarantined defects, metric-specific eligibility, documented AS-IS evidence and bounded text feasibility. Complete history from creation, true labor time, root causes and optimal-action labels remain unavailable; approved metrics explicitly do not require those claims.

Reproduce with `python scripts/validate_process.py`, then `python -m unittest discover -s tests -v`. Evidence includes [validation summary](../reports/milestone2/validation-summary.json), [state reconciliation](../reports/milestone2/state-duration-reconciliation.csv), [publisher audit](../reports/milestone2/publisher-measure-audit.csv) and [conflict register](../reports/milestone2/event-conflicts.csv). Synthetic test fixtures are code-only validation cases and never enter the historical database.
