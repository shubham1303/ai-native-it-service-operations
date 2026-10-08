# Assumption and uncertainty log

| ID | Assumption or uncertainty | Status and validation |
|---|---|---|
| A01 | Ticket/Service/HD Service likely contain much of the support population | Hypothesis. Validate with project/history distribution and sampled text; do not yet exclude every other type. |
| A02 | Earlier cases may have migrated or incomplete histories | Hypothesis prompted by 2007 creation vs 2015 history start. Examine earliest events and closure clusters; migration is not established. |
| A03 | A blank wf_ time might mean an unvisited state | Unconfirmed. Reconcile with wfe_ and extraction logic before filling zeros. |
| A04 | Very long durations may reflect archival/admin processing | Hypothesis, not a diagnosis. Compare cohorts, state coverage and resolution-date concentrations. |
| A05 | Masked identifiers preserve cross-file relationships | Publisher claim partly supported by zero orphan joins. Identity semantics and historical mappings remain unverified. |
| A06 | Sampled conversations can support a bounded future experiment | Conditional. Only 360 issues and many placeholders; evaluate selection bias, case/time split and labeling feasibility. |
| A07 | Observed good outcomes identify optimal actions | Not accepted. Historical actions can be suboptimal; outcome labels alone are insufficient. |
| A08 | Date range metadata is consistent across source documents | Disproved: v3 page and raw issues begin in 2007; source dictionary still says 2016. Raw measured range is used. |
| A09 | A later discovery window reduces legacy-recording distortion | Analysis choice supported by the 2018 concentration; not proof of clean later operations. Starts 2016–2020 and broader types saved for sensitivity. |
| A10 | Source `ended` is a useful boundary for observed interval calculation | Adopted with explicit scope. Cases with later events are excluded. It is not assumed to be an independently verified observation/censoring time for full backlog or survival analysis. |
| A11 | Initial state and owner can be recovered from summaries | Rejected. They are not directly observed before first history update; retain unknown prefix. |
| A12 | Blank state time denotes structural zero when matching publisher visit count is zero | Supported across all inspected state pairs. Allowed only for publisher reconciliation; raw blanks unchanged. Does not fill unobserved initial time. |
| A13 | Ticket label identifies a pure incident population | Rejected. Sample review supports software support, while publisher example includes file exchange. Use support-ticket scope. |
| A14 | Long/repeated Waiting represents preventable delay | Not established after Milestone 4. Multiple necessary dependencies, technical work and administrative time are evidenced; no reviewed episode satisfies the verified-avoidable standard. Outcome C. |
| A15 | Seven calendar days is an operational breach | Rejected. It is a diagnostic threshold; 3/14/30-day sensitivity is reported. No contractual SLA exists in the source. |
| A16 | Repeated-wait duration gap is the time an intervention can save | Rejected. Severity, duration exposure, case selection and confounding remain. No counterfactual measured. |
| A17 | Text process patterns represent all eligible 2022 tickets | Disproved for recurrence rate: 16.8% vs 6.0%. Case-reason labels/evaluation must retain sample restrictions. |

| A18 | Validation → In-progress is a failed-validation/rework label | Rejected as a universal interpretation. Reviewed case 1006849 records successful testing then production deployment. Actual rework also appears outside this exact transition. |
| A19 | Named assignee changes explain most repeated Waiting | Not supported by recorded gaps: handoffs in 88/1,941 assignment-eligible gaps; unrecorded cross-team work remains possible. |
| A20 | A long Waiting episode predicts worse subsequent service | Not established. Pooled recorded reopening/validation-return rates are not higher after long first waits at 3/7/14-day thresholds; incomplete observation and confounding prevent causal or predictive claims. |
| A21 | Diagnostic-information and dependency coordination is the core problem | Stronger specific lead, still unvalidated. Representative burden, ready-to-act time, feasible actor and independent harm require more evidence. |
| A22 | Closed/Resolved always means service restored | Rejected as a universal interpretation. Reviewed text includes nonresponse closure, restoration before status exit and testing/deployment work after resolution labels. |

No assumptions about hourly cost, handling-time savings, SLA targets or automation benefits have been introduced.
