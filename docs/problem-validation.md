# Is there a fixable problem in the waiting time?

Milestone 4, finished 2026-09-11.

## Short answer

No, not from this data. I started this milestone expecting to confirm that Waiting was the problem worth fixing. Waiting is large, and its patterns hold up when I recount them different ways. But it turned out to mix several different activities and dependencies, and neither how long a wait lasts nor how often it repeats tells you whether it was avoidable.

At the end I had three options:

- **A:** Waiting is the problem. Select it.
- **B:** Some other problem has better evidence. Select that instead.
- **C:** The available data can't establish an addressable operational problem.

**I chose C.**

Validation returns didn't work as a replacement (option B). The transition I used to detect them also shows up when testing succeeded and the fix moved on to deployment, not only when investigation had to continue.

The strongest narrower lead is coordination around diagnostic information and dependencies. I haven't verified that those delays are preventable or that they hurt the business.

Two things C doesn't mean. It doesn't prove all waiting is necessary. And I haven't picked an intervention family, an AI task, a savings estimate or a counterfactual benefit.

## What I looked at, and how

I kept the same scope as Milestone 3: 17,132 status-eligible external-project tickets created from 2019 on. I didn't change the raw source files, the eligibility rules, or how I handle tickets whose initial history is unknown. Definitions are in the [metric dictionary](metric-dictionary.md) and the baseline is in [operational discovery](operational-discovery.md).

There are 12,061 observed Waiting entries. 127 of them are zero-duration boundaries, so the episode analysis uses the remaining 11,934 positive intervals across 9,963 tickets. The median episode lasts 4.92 calendar days and p90 is 31.95 days. 4,783 episodes, in 4,387 tickets, last at least seven days. Seven days is a diagnostic cutoff I chose, not an SLA. It also applies per episode, which is different from the cumulative per-ticket waiting threshold in Milestone 3.

When I compare what happened before and after a wait, I only use each ticket's first positive episode, keeping its actual row and any unknown boundaries. Otherwise tickets that wait again and again would get several votes. "Before" counts only include events before the wait started. Messages during the episode are context. Messages and transitions after it ended describe what happened next. Project and priority come from the export, and I can't check what values they had when the wait started, so I use them to describe groups. They aren't validated predictors.

I wrote the [review protocol](milestone4-review-protocol.md) before reading any messages. The sample is deterministic and purposive, spread across projects, and covers 32 distinct tickets: eight each with long/repeated, long/single, short/repeated and short/single Waiting. Two episodes got an expanded review of every message in the episode. I also reviewed all 12 observed Validation → In-progress transitions in the nine primary tickets that have text, within a ±48-hour window. The two reviews share tickets, so this is not 44 independent tickets.

The limits of this review matter a lot:

- These are model-assisted qualitative annotations (an LLM did the first pass). They are **not independent expert or stakeholder validation**.
- Text exists for only 340 primary tickets, all created in 2022, and repeated Waiting is overrepresented among them: 16.8%, against 6.0% of eligible 2022 tickets. So I don't estimate how common any reason is from this purposive sample.
- The excerpts leave out some communications, and technical content is masked.
- The review registers keep the comment IDs, source rows, timing, counterevidence and packet hashes behind every judgment.

## 1. What Waiting actually is

The event log just says `waiting`. It doesn't record a reason, who the dependency is on, a due time, or when the ticket became ready to move. There are separate Validation, Pending deployment and Resolved under monitoring states, but the messages show those same activities also happen while a ticket sits in Waiting. So time in a status isn't a clean measure of inactivity.

This is what I saw going on inside Waiting episodes:

| What was going on | Where I saw it (ticket: comment IDs) | What it shows |
|---|---|---|
| Missing or unsuitable diagnostic material | Case 1007739: comments 1095949, 1096016, 1096543, 1097399 | Logs came from the wrong directory and dates; collecting them again ran into size, extraction and infrastructure constraints. |
| Customer testing and approval | 1005715: 1063924, 1065592; 1010562: 1111478, 1111502 | UAT, business confirmation and production approval/deployment are separate stages. Some of that work happens during Waiting. |
| Access and technical dependencies | 1010058: 1110389, 1112403; 1006856: 1075779 | DNS, report access and network connectivity can block progress. |
| Coordinating people and sessions | 1004444: 1047956, 1048059; 1010058 expanded review | Sessions can fail because test access is missing or another team isn't available. |
| Internal investigation or development | 1007739: 1099917; 1007010: 1076618, 1076941 | Engineers can be investigating while the ticket says Waiting. |
| Intermittent recurrence and monitoring | 1004368: 1060323, 1060351; 1007010: 1076941 | Getting evidence may require the symptom to come back; watching can be deliberate. |
| Scheduled activity or release decisions | 1005454: 1065126; 1009327: 1107904 | Scheduling and approval constraints can be legitimate. |
| Confirmation and administrative closure | 1004519: 1070154; 1010058: 1121152; 1005127: 1055109 | No response can lead to closure, and restoration can come before the status change. Closure and recovery are different outcomes. |

These are provisional mechanisms. They overlap, and they aren't ground-truth labels. One episode can also change reason partway through. Case 1010058 goes from session and access problems, to having UAT report access, to waiting on business testing, to closure for nonresponse, all within one 65-day Waiting interval. Blaming all 65 days on the initial DNS problem would be wrong.

## 2. Which waits were necessary, and which might be fixable

Some waits look like real prerequisites: getting the relevant logs, waiting for an intermittent symptom to come back, production approval, testing, access to the customer's environment, and watching a deployed change. But a real prerequisite **doesn't** mean the whole interval was necessary.

The clearest leads for something fixable are incomplete diagnostic evidence, coordinating access or getting the right people together, and communication once a prerequisite has been met. Case 1007739 shows most of it: wrong logs, a corrected request, an objection to the file size, a narrower request that support had already supplied, an extraction problem that needed infrastructure people, and investigation that kept going. That's a reason to look into diagnostic readiness. It doesn't show there was a known, feasible faster route.

In case 1005127 the customer confirms that clearing the cache worked before the Waiting ends. That's an administrative tail, but it isn't evidence of ongoing service harm or an unjustified handling delay. Case 1007567 has a four-second Waiting interval followed by Resolved, while feedback is still being requested later. Tidying up timestamps like these wouldn't show that service improved.

**None of the episodes I reviewed meets the verified-avoidable standard.** What's missing is validated response expectations, whether people were available and had the authority to act, when prerequisites were actually completed, the full communications, and a defensible comparison. That's a statement about the evidence I reviewed. It isn't an avoidability rate for the population, and it doesn't mean the operation has no waste.

## 3. What comes before a long wait

Looking at each ticket's first positive episode, these are the descriptive associations:

| Before entry / recorded characteristic | Tickets | Share with first episode ≥7 days |
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

Tickets that were in Validation right before Waiting have longer first waits, but they're a small group with a different makeup. When I require at least five tickets on each side within year × recorded priority × project, only six strata overlap. They cover just 63 of the 213 Validation-preceded tickets and 225 of the 8,143 In-progress-preceded ones. The long-wait rate after Validation is higher in three strata, lower in two, and equal in one. That isn't enough to support a general causal explanation or a prediction anyone could deploy.

More named handoffs don't steadily raise the rate. Recorded Blocker and Highest priority tickets actually have lower first-long-wait rates (31.0% and 32.6%) than Medium (41.4%). Prioritization, case mix or recording habits could explain that, and it doesn't prove Medium tickets have removable delays. Small categories stay in the exports, but I don't treat them as strong signals.

The data identifies projects and masked individual assignees. It doesn't reliably map teams, queues, capacity, skills or how the organization was structured at the time. A project isn't a team, and a handoff between named people isn't a group transfer. So I can't attribute delay directly to queueing or staffing.

## 4. What makes waiting repeat

Under the original repeat definition, 1,299 tickets have 1,990 gaps between Waiting entries. These are the most common exact paths:

| Between-wait path | Gap occurrences | Tickets with this path |
|---|---:|---:|
| Waiting → In-progress → Waiting | 976 | 707 |
| Waiting → In-progress → Validation → In-progress → Waiting | 237 | 206 |
| Waiting → Validation → Waiting | 204 | 162 |
| Waiting → Resolved → Waiting | 74 | 63 |
| Waiting → Pending deployment → Waiting | 56 | 49 |

One ticket can have several paths, so the ticket counts can't be added up. The first path makes up 49.0% of gaps. It fits repeated clarification, technical work alternating with dependencies, or coarse use of statuses, and the path alone can't tell those apart.

A validation return sits between waits in 294 of 1,990 gaps (14.8%), in 251 of the 1,299 repeated-wait tickets (19.3%). A named handoff happens in 88 of 1,941 assignment-eligible gaps (4.5%), in 86 tickets. 1,591 (82.0%) of those eligible gaps have neither. During Waiting itself, 793 of 11,700 assignment-eligible intervals contain a named handoff (6.8%). So recorded handoffs and validation returns, as I defined them, don't explain most of the repetition. Cross-team work that never got recorded is still possible.

I also checked how much the boundaries matter. 1,284 tickets still count as repeated when both episodes have to be positive, 1,185 when each lasts over a minute, and 1,040 when each lasts over an hour. Repetition isn't just a zero-duration artifact, but very short status changes do inflate a literal count. None of these cutoffs identifies waste.

## 5. Who's in the 7.6%

The original 1,299 repeated-wait tickets still account for 25.18% of pooled Waiting time. I defined this group by looking back at complete histories, so these tickets wouldn't necessarily be recognizable when they arrive.

- **Time:** 670 (51.6%) were created in 2019–2020, against 35.6% of the status cohort. The repeat rate falls from 12.4% in 2019 to 6.0% in 2022. The incomplete 2023 has 5.0%, with less time for repeats to build up.
- **Priority:** 874 (67.3%) are Medium, against 64.0% of the cohort. Blocker accounts for 30 tickets and Highest for 98. The concentration isn't simply the most urgent tickets.
- **Projects:** repeats occur in 173 projects. The top ten by repeat count hold 612 tickets (47.1%). C12hgx18a contributes 118 of 654 tickets (an 18.0% repeat rate), C06hgfz_x 77 of 324 (23.8%), and C10ggx1nv 49 of 106 (46.2%). None of this shows a team underperforming.
- **Validation:** 303 repeated tickets have a validation return somewhere in their history, but only 251 have one specifically between Waiting episodes. Appearing in the same ticket is weaker evidence than appearing in the right place in time.

No single characteristic I could observe picks out all or most repeated tickets as one fixable failure. Older history, project mix, complexity, more chances to re-enter states, and workflow practice changing over time all remain plausible. The full characteristic register keeps the denominators, so small projects aren't ranked on raw rates alone.

## 6. Validation returns: a separate problem, or part of waiting?

There are 827 Validation → In-progress events in 672 tickets. Waiting comes immediately after 516 of them (62.4%), and 534 (64.6%), in 452 tickets, are followed by Waiting within seven days. So it's a common path. Together with the between-wait numbers above, returns explain a **subset** of repeated waiting, not waiting in general.

I can't call all of these events rework. The 12 returns with text include delivering a fix, coordinating deployment, investigation that kept going, and context I couldn't determine. Case 1006849 explicitly records successful testing and approval before the return, then production scheduling and deployment. Case 1004667 is about a new logo change and assignment. One return in 1007420 has no comments within the review window. Across the whole cohort, 72 of the 827 returns come after less than a minute in Validation, so what the state means still needs checking.

Real rework also shows up without this exact transition. Case 1008607 reports a UAT error and another development fix while moving Waiting → Validation. So the event is neither a verified defect label nor a complete count of rework. And 545 of the 672 return tickets were created in 2019–2020, which limits what the 2022 text can tell me.

Validation returns are still worth looking into, but on this evidence they **can't replace waiting as a validated core problem**.

## 7. What happens after a long wait

I didn't want to measure harm with a duration that already includes the wait. So I compared recorded reopenings and validation returns strictly after the first positive Waiting episode ends, within 30 days. I count one first episode per ticket and leave out the six episodes with no observed exit.

| First episode | Exited tickets | Recorded reopening within 30 days | Recorded validation return within 30 days |
|---|---:|---:|---:|
| Less than seven days | 6,011 | 145 (2.41%) | 180 (2.99%) |
| At least seven days | 3,946 | 84 (2.13%) | 57 (1.44%) |

Three- and fourteen-day cutoffs also show no higher pooled rate in the long-wait group, and reopening doesn't move in the same direction every year. Long first waits go straight to Resolved or Closed in 3,221 of 3,946 cases (81.6%), and short ones in 4,524 of 6,011 (75.3%). Those statuses don't confirm the problem was actually fixed.

These are **associations between recorded events, not validated forecasts or complete 30-day incidence estimates**. The end of the export isn't a verified follow-up period, and new tickets or complaints made outside the platform may be missing. If I keep only tickets whose source data runs at least 30 days past the exit, 888 are left. Reopening is then 4.55% for long waits against 5.84% for short ones, and validation returns are 9.36% against 17.90%. That restriction selects long-lived or ongoing tickets, and it doesn't solve censoring or confounding.

So in these comparisons, long Waiting doesn't come with worse pooled recorded outcomes. That doesn't make waiting protective or entirely legitimate. For this comparison I don't have independently measured restoration, user harm, verified SLA breaches, repeat contacts across linked tickets, or reliable satisfaction data. Longer total ticket duration isn't a substitute for any of them.

## Weighing the candidates

| Candidate | Evidence for | Competing explanation / still unverified | Decision |
|---|---|---|---|
| Concentrated long/repeated Waiting | Large, robust concentration; recurring paths | A mix of necessary dependencies, active work and admin; readiness and harm unknown | Not A. The size is established; whether it's fixable isn't. |
| Validation returns / rework | Often followed by Waiting; behind a subset of recurring paths | Successful testing and deployment can use this transition, and real rework can use others; concentrated in older history | Not B, at least not on this proxy. |
| Diagnostic-information and dependency coordination | Direct evidence of wrong or incomplete logs, extraction and access constraints, scheduling, and changing prerequisites | No representative frequency, verified input standard, accountable ready actor, feasible faster alternative or independent harm | Strongest narrower lead, but not a validated replacement. |
| What states and closures mean, and incomplete outcomes | Technical work during Waiting; restoration before exit; closure for nonresponse | A measurement limitation doesn't by itself prove a business problem, or that a tool would help | Needs resolving before any problem can be validated reliably. |

**So the decision is C.** I keep the baseline, but I replace the assumption "reduce waiting" with a narrower question: **When diagnostic information or a dependency is ready, does a controllable coordination failure delay a feasible next action and cause a meaningful adverse outcome?** That's a question to answer. I'm not claiming the problem exists.

## 8. What it would take to call a delay avoidable

The [avoidability evidence standard](avoidability-evidence-standard.md) lists what I'd need: when reasons changed and prerequisites were completed, an accountable actor who was authorized and available, an agreed time expectation, the complete linked communications, any competing dependencies, and an independently measured adverse outcome. A defensible comparison also has to separate technical work, necessary testing and change windows, and admin time from a gap someone could have controlled.

The next step would be to collect and judge that evidence on a consecutive or probability-based sample, comparing long against short and repeated against single waits. That sample should include disputed and necessary waits, have state meanings checked with process owners, and keep unknown labels as unknown. If the operational evidence can't be had, I'd keep this as an observational study or find a more suitable dataset, and I wouldn't claim an operational improvement project has been validated.

Process redesign, deterministic rules, traditional automation and AI all stay off the table until a business problem is selected and validated. I haven't estimated savings, because shorter waits among peer tickets, gaps in average duration and hypothetical percentage reductions aren't defensible counterfactuals.

## Reproducing this, and where the evidence is

- [Episode summary](../reports/milestone4/mechanism-summary.json), [positive episodes](../reports/milestone4/waiting-episodes.csv), [boundary paths](../reports/milestone4/waiting-boundary-paths.csv).
- [First-wait antecedents](../reports/milestone4/first-wait-antecedents.csv), [overlap strata](../reports/milestone4/preceding-state-overlap-strata.csv), [repeat characteristics](../reports/milestone4/repeated-case-characteristics.csv), [between-wait paths](../reports/milestone4/between-wait-paths.csv).
- [Downstream outcomes](../reports/milestone4/first-wait-downstream-outcomes.csv), [threshold sensitivity](../reports/milestone4/downstream-threshold-sensitivity.csv), [year breakdown](../reports/milestone4/downstream-by-year.csv). The year export includes all first positive episodes, including the six with no observed exit, so use the exited-ticket denominators for the main comparison.
- [Waiting review register](../reports/milestone4/waiting-review-register.json), [validation review register](../reports/milestone4/validation-review-register.json), [review metadata](../reports/milestone4/review-metadata.json). The registers link each judgment to the original comment IDs and source rows, and the packets keep the text I inspected along with its timing.

Run `python scripts/validate_mechanisms.py`, then `python scripts/record_mechanism_review.py`, then `python -m unittest discover -s tests -v`. The numbers regenerate from the read-only validated database. The qualitative judgments are written out explicitly in the review script rather than inferred by it, and pinned packet hashes stop them from being silently reused if the evidence changes. The tests cover duration reconciliation, adjacent states, unknown prefixes, time boundaries, per-ticket denominators and where each review judgment came from. Synthetic test fixtures never get mixed into the historical data.
