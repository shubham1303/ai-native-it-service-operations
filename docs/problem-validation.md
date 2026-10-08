# Milestone 4: problem validation and root-cause analysis

Completed 2026-09-11. **Decision C: the available data is insufficient to establish an addressable operational problem.**

Waiting is substantial and its recorded patterns are reproducible. It contains several different activities and dependencies, however, and neither duration nor repetition establishes avoidable delay. Validation returns do not provide a better validated replacement: the recorded transition can represent successful testing followed by deployment as well as continuing investigation. The strongest narrower lead is diagnostic-information and dependency coordination, but its preventability and business impact remain unverified.

This is the completed milestone decision. It does not prove that all waiting is necessary. No intervention family, AI task, savings estimate or counterfactual benefit has been selected.

## Evidence and method

The scope remains 17,132 status-eligible external-project Ticket records created from 2019 onward. Raw source files, eligibility decisions and unknown initial history remain unchanged. See [Milestone 2 definitions](metric-dictionary.md) and [Milestone 3 baseline](operational-discovery.md).

There are 12,061 observed Waiting entries, including 127 zero-duration boundaries. The episode analysis uses 11,934 positive intervals in 9,963 cases. Median positive episode duration is 4.92 calendar days; p90 is 31.95 days. There are 4,783 episodes lasting at least seven days in 4,387 cases. Seven days is a diagnostic threshold, not an SLA. This episode threshold differs from Milestone 3's cumulative per-case waiting threshold.

Antecedent and downstream comparisons select the first positive episode per case, preserving its actual row and unknown boundaries. This avoids giving repeatedly waiting cases multiple votes. Prefix event counts use only events before entry; during-episode messages describe context; post-exit messages and transitions describe subsequent behavior. Project and priority are export attributes whose historical values at entry cannot be verified, so they are descriptive strata, not validated prospective predictors.

The [review protocol](milestone4-review-protocol.md) was written before message review. A deterministic, project-diverse purposive sample covers 32 distinct cases: eight each with long/repeated, long/single, short/repeated and short/single Waiting. Two episodes received expanded full-episode message review. All 12 observed Validation → In-progress transitions in the nine text-covered primary cases were also reviewed within a ±48-hour window. The reviews overlap in cases and are not 44 independent tickets.

These are model-assisted qualitative annotations, **not independent expert or stakeholder validation**. Text exists for only 340 primary cases, all created in 2022; repeated Waiting is overrepresented, at 16.8% versus 6.0% of eligible 2022 cases. No reason prevalence is extrapolated from the purposive review. Excerpts omit some communications and technical content is masked. Comment IDs, source rows, temporal position, counterevidence and packet hashes are retained in the review registers.

## 1. What Waiting actually represents

The event log records one `waiting` value without a reason, dependency owner, due time or readiness event. Separate Validation, Pending deployment and Resolved under monitoring states exist, but messages show that their associated activities can also occur during Waiting. Status time is not a clean measure of inactivity.

| Observed mechanism | Episode-local evidence | What the evidence establishes |
|---|---|---|
| Missing or unsuitable diagnostic material | Case 1007739: comments 1095949, 1096016, 1096543, 1097399 | Wrong log directory/dates; subsequent collection faced size/extraction and infrastructure constraints. |
| Customer testing and approval | 1005715: 1063924, 1065592; 1010562: 1111478, 1111502 | UAT, business confirmation and production approval/deployment are distinct stages. Some work occurs during Waiting. |
| Access and technical dependencies | 1010058: 1110389, 1112403; 1006856: 1075779 | DNS, report access and network connectivity can block progress. |
| Coordinating people and sessions | 1004444: 1047956, 1048059; 1010058 expanded review | Sessions can fail because test access or another team's availability is missing. |
| Internal investigation or development | 1007739: 1099917; 1007010: 1076618, 1076941 | Engineers can be investigating while a ticket says Waiting. |
| Intermittent recurrence and monitoring | 1004368: 1060323, 1060351; 1007010: 1076941 | Evidence may require symptom recurrence; observation can be purposeful. |
| Scheduled activity or release decisions | 1005454: 1065126; 1009327: 1107904 | Scheduling and approval constraints can be legitimate. |
| Confirmation and administrative closure | 1004519: 1070154; 1010058: 1121152; 1005127: 1055109 | Nonresponse can lead to closure; restoration can also precede the status change. Closure and recovery are different outcomes. |

These are multiple provisional mechanisms, not mutually exclusive ground-truth labels. One episode can change reason: case 1010058 moves through session/access problems, available UAT report access, pending business testing, and eventual nonresponse closure across one 65-day Waiting interval. Assigning all 65 days to the initial DNS problem would be incorrect.

## 2. Necessary versus potentially addressable periods

Specific prerequisite waits appear plausible: relevant logs, reproduction of intermittent symptoms, production approval, testing, customer-environment access, and observation of a deployed change. Their existence does **not** establish that the entire interval was necessary.

The clearest addressability leads concern incomplete diagnostic evidence, coordination to obtain access or the right participants, and communication after a prerequisite is satisfied. Case 1007739 shows wrong logs, a corrected request, a file-size objection, a narrowed request already supplied by support, an extraction problem needing infrastructure participation, and continued investigation. This supports investigating diagnostic readiness; it does not establish a known feasible faster route.

Case 1005127 contains a customer confirmation that cache clearing worked before Waiting ended. This identifies an administrative tail, but not ongoing service harm or an unjustified handling delay. Case 1007567 has a four-second Waiting interval followed by Resolved while feedback is still requested later. Optimizing these timestamps would not establish improved service.

**No reviewed episode satisfies the verified-avoidable standard.** Missing elements include validated response expectations, actor availability and authority, prerequisite completion times, full communications, and a defensible comparison. This concerns the reviewed evidence; it is neither a population avoidability rate nor a conclusion that the operation has no waste.

## 3. What precedes long waiting

First positive episodes provide these descriptive associations:

| Before entry / recorded characteristic | Cases | Share with first episode ≥7 days |
|---|---:|---:|
| Previous state In-progress | 8,143 | 38.1% |
| Previous state Validation | 213 | 62.9% |
| Previous state unknown | 1,486 | 44.5% |
| No prior Validation → In-progress transition | 9,711 | 39.5% |
| One prior validation return | 235 | 45.1% |
| Two or more prior validation returns | 17 | 52.9% |
| No prior named assignee handoff, assignment eligible | 4,239 | 41.9% |
| One prior named handoff | 4,037 | 36.4% |
| Two or more prior named handoffs | 1,386 | 38.2% |

Validation immediately before Waiting is associated with a longer first wait, but it is a small, differently composed group. Requiring at least five cases on each side within year × recorded priority × project leaves six overlapping strata, covering only 63/213 Validation-preceded and 225/8,143 In-progress-preceded cases. Three strata have a higher long-wait rate after Validation, two lower, and one equal. This is inadequate support for a general causal explanation or deployable prediction.

There is no monotonic increase with prior named handoffs. Recorded Blocker and Highest priorities have lower first-long-wait rates (31.0% and 32.6%) than Medium (41.4%). Prioritization, case mix and recording practices could explain this; it does not prove removable delays in Medium tickets. Small categories are retained in exports but not treated as strong signals.

The data identifies projects and masked individual assignees, not reliably mapped teams, queues, capacity, skills or historical organizational structures. A project is not a team; a named handoff is not a group transfer. Direct queueing or staffing attribution is unsupported.

## 4. What creates repeated waiting

The original repeat definition identifies 1,299 cases and 1,990 gaps between Waiting entries. The most common exact paths are:

| Between-wait path | Gap occurrences | Cases with this path |
|---|---:|---:|
| Waiting → In-progress → Waiting | 976 | 707 |
| Waiting → In-progress → Validation → In-progress → Waiting | 237 | 206 |
| Waiting → Validation → Waiting | 204 | 162 |
| Waiting → Resolved → Waiting | 74 | 63 |
| Waiting → Pending deployment → Waiting | 56 | 49 |

Cases can contribute several paths; case counts must not be added. The first path accounts for 49.0% of gaps. It is consistent with repeated clarification, alternating technical work and dependencies, or coarse status use; the path alone cannot distinguish them.

A validation return occurs between waits in 294/1,990 gaps (14.8%), involving 251/1,299 repeated-wait cases (19.3%). A named handoff occurs in 88/1,941 assignment-eligible gaps (4.5%), involving 86 cases. Of these eligible gaps, 1,591 (82.0%) contain neither a validation return nor a named handoff. During Waiting itself, 793/11,700 assignment-eligible intervals contain a named handoff (6.8%). Recorded handoffs and the defined validation-return transition therefore do not explain most recurrence. Unrecorded cross-team work remains possible.

Boundary sensitivity retains 1,284 repeated cases when both episodes must be positive, 1,185 when each exceeds one minute, and 1,040 when each exceeds one hour. Repetition is not solely a zero-duration artifact, but very short changes inflate a literal recurrence count. None of these diagnostic thresholds identifies waste.

## 5. Characteristics of the 7.6% concentration group

The original 1,299 repeated-wait cases still contribute 25.18% of pooled Waiting time. They are a retrospective group defined using complete observed histories, not necessarily identifiable when a ticket arrives.

- **Time:** 670 (51.6%) were created in 2019–2020, compared with 35.6% of the status cohort. Repeat rates decline from 12.4% in 2019 to 6.0% in 2022; incomplete 2023 has 5.0% and less opportunity to accumulate recurrence.
- **Priority:** 874 (67.3%) are Medium, compared with 64.0% of the cohort. Blocker accounts for 30 cases, Highest for 98. The concentration is not simply the most urgent tickets.
- **Projects:** repeats occur in 173 projects. The top ten by repeat-case count contain 612 cases (47.1%). C12hgx18a contributes 118/654 tickets (18.0% repeat rate); C06hgfz_x contributes 77/324 (23.8%); C10ggx1nv contributes 49/106 (46.2%). These associations do not establish team underperformance.
- **Validation:** 303 repeated cases have a validation return somewhere in their history, but only 251 have one specifically between Waiting episodes. Co-occurrence is weaker evidence than temporal placement.

No single observed characteristic identifies all or most repeated cases as one addressable failure mechanism. Older history, project mix, complexity, opportunity to re-enter states and changing workflow practice remain plausible explanations. The full characteristic register preserves denominators rather than ranking small projects by raw rates alone.

## 6. Validation returns: separate problem or waiting mechanism?

There are 827 Validation → In-progress events in 672 cases. Waiting is the immediate next state after 516 events (62.4%); 534 events (64.6%), in 452 cases, are followed by Waiting within seven days. This establishes a frequent temporal pathway. Combined with the between-wait results, returns are a mechanism for a **subset** of repeated waiting, not a general explanation.

Calling all these events rework is not justified. The 12 text-covered returns include fix delivery, deployment coordination, continuing investigation and unknown context. Case 1006849 explicitly records successful testing and approval before the return, followed by production scheduling and deployment. Case 1004667 concerns a new logo change and assignment. One return in 1007420 has no comments within the review window. Across the full cohort, 72/827 returns follow less than one minute in Validation; state meaning requires verification.

Actual rework can also appear without this exact return: case 1008607 reports a UAT error and a further development fix while moving Waiting → Validation. The event proxy is neither a verified defect label nor a complete census of rework. The 545/672 return cases created in 2019–2020 further limit inference from available 2022 text.

Validation returns remain worth investigating, but **cannot replace waiting as a validated core problem** on this evidence.

## 7. Downstream outcomes after long waiting

To avoid defining harm using a duration that already includes the wait, compare recorded reopening and validation-return events strictly after the first positive Waiting exit, within 30 days. Count one first episode per case; six episodes without an observed exit are excluded.

| First episode | Exited cases | Recorded reopening within 30 days | Recorded validation return within 30 days |
|---|---:|---:|---:|
| Less than seven days | 6,011 | 145 (2.41%) | 180 (2.99%) |
| At least seven days | 3,946 | 84 (2.13%) | 57 (1.44%) |

Three- and fourteen-day thresholds also show no higher pooled rate in the long-wait group. Year-specific reopening directions are not uniform. Direct transitions to Resolved or Closed follow 3,221/3,946 long first waits (81.6%) and 4,524/6,011 short first waits (75.3%); these statuses do not verify recovery.

These are **recorded-event associations, not validated forecasts or complete 30-day incidence estimates**. The source endpoint is not a verified follow-up contract, and new tickets or off-platform complaints may be missing. Restricting to cases whose source endpoint extends at least 30 days after exit leaves only 888 cases: reopening is 4.55% for long versus 5.84% for short, and validation returns 9.36% versus 17.90%. This selects long-lived or continuing cases and does not solve censoring or confounding.

Long Waiting therefore does not show worse pooled recorded outcomes in these comparisons. This cannot establish that waiting is protective or entirely legitimate. Independently measured restoration, user harm, verified SLA breaches, repeat contacts across linked tickets and reliable satisfaction outcomes are unavailable for this comparison. Longer total ticket duration is not a substitute for those outcomes.

## Candidate comparison and decision

| Candidate | Evidence in favor | Competing explanation / missing validation | Decision |
|---|---|---|---|
| Concentrated long/repeated Waiting | Large, robust concentration; recurring paths | Mixed necessary dependencies, active work and administration; readiness and harm unknown | Do not select A. Magnitude is established; addressability is not. |
| Validation returns / rework | Often followed by Waiting; subset of recurring paths | Successful testing/deployment can use this transition; genuine rework can use others; historical concentration | Do not select B on this proxy. |
| Diagnostic-information and dependency coordination | Direct evidence of wrong/incomplete logs, extraction/access constraints, scheduling and changing prerequisites | No representative frequency, verified input standard, accountable ready actor, feasible faster alternative or independent harm | Strongest narrower mechanism lead, but not a validated replacement. |
| State/closure meaning and incomplete outcomes | Technical work during Waiting; restoration before exit; nonresponse closure | Measurement limitation does not itself prove an operational business problem or benefit from a tool | Prerequisite to reliable problem validation. |

**Select C.** Preserve the baseline, but replace the assumption “reduce waiting” with the bounded validation question: **When diagnostic information or a dependency is ready, does a controllable coordination failure delay a feasible next action and cause a meaningful adverse outcome?** This is a question, not an asserted problem.

## 8. Evidence needed to classify delay as avoidable

The [avoidability evidence standard](avoidability-evidence-standard.md) specifies the required record: reason changes and prerequisite completion, an accountable authorized and available actor, an agreed time expectation, complete linked communications, competing dependencies, and an independently measured adverse outcome. A defensible comparison must separate technical work, necessary testing/change windows and administrative time from a controllable gap.

The next stage should obtain and adjudicate this evidence across a consecutive or probability-based sample with long/short and repeated/single comparisons. Include disputed and necessary waits, verify state meanings with process owners, and preserve unknown labels. If operational evidence is unavailable, retain an observational study or obtain a more suitable dataset; do not claim that an operational improvement project has been validated.

Process redesign, deterministic rules, traditional automation and AI evaluation remain gated until the business problem is selected and validated. No savings are estimated: shorter peer waits, average duration gaps and hypothetical percentage reductions are not defensible counterfactuals.

## Reproducibility and evidence map

- [Episode summary](../reports/milestone4/mechanism-summary.json), [positive episodes](../reports/milestone4/waiting-episodes.csv), [boundary paths](../reports/milestone4/waiting-boundary-paths.csv).
- [First-wait antecedents](../reports/milestone4/first-wait-antecedents.csv), [overlap strata](../reports/milestone4/preceding-state-overlap-strata.csv), [repeat characteristics](../reports/milestone4/repeated-case-characteristics.csv), [between-wait paths](../reports/milestone4/between-wait-paths.csv).
- [Downstream outcomes](../reports/milestone4/first-wait-downstream-outcomes.csv), [threshold sensitivity](../reports/milestone4/downstream-threshold-sensitivity.csv), [year breakdown](../reports/milestone4/downstream-by-year.csv). The year export includes all first positive episodes, including the six without an observed exit; use exited-case denominators for the main comparison.
- [Waiting review register](../reports/milestone4/waiting-review-register.json), [validation review register](../reports/milestone4/validation-review-register.json), [review metadata](../reports/milestone4/review-metadata.json). Registers link judgments to original comment IDs and source rows; packets preserve inspected text and temporal context.

Run `python scripts/validate_mechanisms.py`, then `python scripts/record_mechanism_review.py`, and `python -m unittest discover -s tests -v`. Quantitative results regenerate from the read-only validated database. Qualitative judgments are explicitly authored, not inferred by the script; pinned packet hashes prevent reusing them silently after evidence changes. Tests cover duration reconciliation, adjacent states, unknown prefixes, time boundaries, case-level denominators and review-source lineage. Synthetic fixtures never enter historical data.
