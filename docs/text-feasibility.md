# Text sample: scope and future evaluation feasibility

The source contains 360 issues with utterances, all created in 2022. Of these, 340 are Ticket records in the primary population and all 340 pass status-timeline checks. Only 322 pass assignment-history eligibility. The remaining 20 text cases comprise 10 HD Service and 10 Deployment records.

The appraisal workbook has 747 rows for 361 unique issues. All text cases join to appraisal cases; one appraisal case has no supplied utterances. No duplicate issue/comment/utterance keys or inconsistent within-comment author, role, sequence or timestamp metadata were detected. One utterance is timestamped after the supplied case endpoint and recorded resolution. Future evaluation must exclude any message unavailable at its decision cutoff regardless of the case's other eligibility.

## Qualitative check

A deterministic eight-case sample was selected from the text-bearing Ticket records with seed 20260911. We reviewed the first comment's supplied utterances. This is a plausibility check of the masked domain, not a representative prevalence estimate or a gold-label exercise.

| Issue ID | What the supplied opening comment supports |
|---|---|
| 1004444 | Date inconsistency reported after an upgrade; cause unverified |
| 1005729 | Incomplete reference to an encountered issue; insufficient standalone context |
| 1006726 | Browser/login compatibility troubleshooting request |
| 1007473 | Slow report-download complaint |
| 1008458 | Brief Android QR scanning error report |
| 1009328 | Audit/security-related change request with technical detail masked |
| 1009623 | Empty application page report |
| 1009637 | Failed processing with a described retry workaround |

These support a customer software-support interpretation and demonstrate variation in available information. They do not establish safe fixes, incident categories for the full export, or avoidable resolution delays. The publisher's worked example (1004364) also explicitly describes a file-sharing case within Ticket records. The operational scope must therefore include coordination/administrative use rather than claim a pure incident population.

## Sampling and leakage limitations

The 340 sampled primary tickets have a recorded Medium-priority share of 42.65%, compared with 42.01% in the 2022 primary population. This is one descriptive comparison, not proof of representativeness. The full primary population's Medium share is 64.13%, illustrating why comparisons must be time-matched. Project, length, outcome and selection differences still require examination if a text intervention is proposed. Source sampling was designed for appraisal, not our future use case.

Messages contain repeated greetings, signatures, placeholders and policy/template text. A template asking whether root cause was understood is not evidence that root cause was actually established. Role `others` does not identify a specialist or manager reliably. Existing Q1/Q2/Q3 appraisal scores are not correct-action, diagnosis or safe-remediation labels.

## Permitted future experiment design

- Start from a justified operational question. Text availability alone does not justify an LLM.
- Preserve an independent issue-level split. All comments/utterances from an issue stay together. Use time ordering and adequate observation windows; do not lock a final split before the task and label are defined.
- Build each input from information available at the decision timestamp. Final resolution, later messages and aggregate lifetime fields stay out of early-decision inputs.
- Construct a reviewed task-specific rubric and labels if the historical source lacks them. Report annotation uncertainty and independent test-case counts.
- Compare against rules or a simpler model. Report performance only on the eligible sampled population, with uncertainty appropriate to the small test set.
- Keep technical content masking visible. No grounded test of password resets, SQL fixes, infrastructure changes or executable resolution advice is possible from placeholders alone.

Feasibility verdict: **sufficient to consider a small, clearly scoped communication/process-assistance experiment later; insufficient for broad autonomous remediation claims.** No AI task, annotation labels or model performance has been created.

## Milestone 3 addendum

The primary text sample contains 57 repeated-wait cases out of 340 (16.8%), compared with 325/5,404 (6.0%) in the eligible 2022 population. Long Waiting is also enriched: 146/340 (42.9%) versus 1,408/5,404 (26.1%). Similar priority proportions do not make the sample representative of process complexity. Carry this selection bias into any label review or evaluation; see reports/milestone3/text-candidate-coverage.csv.
