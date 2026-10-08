# Milestone 4 review protocol

Written before episode/message review. Objective: explain waiting mechanisms and assess evidence of addressability, without presuming that reducing waiting is beneficial. Do not evaluate interventions or estimate savings in this milestone.

## Units and scope

Use the validated status cohort and positive-duration Waiting episodes. Preserve zero-duration boundaries as a sensitivity check, not substantive delays. Episode observations are nested within issues; case-level comparisons use one first eligible episode per issue. Compare ≥7-calendar-day episodes with shorter episodes, checking 3/14-day thresholds. This differs from Milestone 3's cumulative per-ticket threshold and must be labeled.

Events before entry describe possible antecedents. Events during the episode are context, not pre-entry predictors. Events after exit describe downstream behavior, not causes of entering Waiting. Unknown timestamps, owner identity and intent remain unknown.

## Mechanism rubric

Multiple provisional labels allowed: customer information/logs requested; customer testing/confirmation; internal technical work; third-party dependency; planned deployment/change; planned monitoring; coordination/meeting; administrative closure/nonresponse; unknown. A Waiting state or keywords alone do not establish a reason. Link a label to actual episode-local messages and their timestamps.

Addressability categories:

- Necessary dependency appears plausible: specific evidence of information, testing, scheduled work or another prerequisite. Does not prove all elapsed time was necessary.
- Potentially addressable portion: evidence of an action available to an identified actor with a later observed action gap. Does not prove avoidable delay without expected response time, authority, resources and complete communications.
- Insufficient evidence: masked, sparse, templated or conflicting context prevents a defensible determination.

No case receives a verified-avoidable label unless evidence establishes the prerequisite was satisfied, a feasible authorized action existed, the responsible actor was available, a reasonable time standard was exceeded, competing dependencies were absent, and the proposed comparison/counterfactual is defensible.

## Text review design

Select up to eight distinct issues in each stratum: long episode/repeated Waiting, long episode/single Waiting, short episode/repeated Waiting and short episode/single Waiting. Use deterministic project-diverse selection with seed 20260911; one episode per sampled case. These are purposive comparisons within the biased 2022 text sample, not a population prevalence sample. Include both sides of episode boundaries in context but mark post-exit material separately.

Review the latest three comments from the prior 48 hours, and up to four comments distributed through the episode, plus the first post-exit comment within 48 hours. Save exact comment IDs and source rows. Context excerpts are incomplete when long; absence of evidence is not evidence of no communication. Expand a case when snippets are insufficient. Do not use template policy text as verified operating policy or assume reminders were sent.

All judgments are model-assisted qualitative annotations, not independent human labels or stakeholder validation. Reviewer sees selection stratum; no blinding is claimed.

## Quantitative checks and decision gate

Compare preceding states, prior validation returns, prior named handoffs, project/year/recorded-priority mix, between-wait paths and retrospective concentration. Analyze first-episode downstream outcomes separately from elapsed resolution to avoid a part-whole timing argument. Keep follow-up completeness limitations and case/project dependence explicit.

Compare long/repeated Waiting, validation returns and any stronger observed mechanism. Choose A/B only with evidence of a concrete addressable problem, not merely a timing association or a plausible tool. Choose C if mechanisms can be described but addressability cannot be established. C is a completed evidence decision, not failure to finish the milestone.
