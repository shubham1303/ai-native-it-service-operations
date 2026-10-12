# What would count as an avoidable delay

Milestone 4 ended with decision C: this data can't establish an addressable problem (see [problem-validation.md](problem-validation.md)). This page sets out what extra evidence would be needed to change that. It isn't a redesigned workflow, an approved policy or a proposed intervention.

The basic rule: a long interval only tells you where to look. I'd call it a verified avoidable delay only once there's support for four things: someone could feasibly have acted earlier, it was their responsibility, there was an expected time for it, and the delay had a consequence. A necessary prerequisite doesn't make all the elapsed time necessary. And a lack of comments doesn't mean nobody was working.

## The evidence I'd need for each episode

| What has to be established | Evidence to get | Why the current data falls short |
|---|---|---|
| The actual reason, and when it changed | Dated dependency history, the specification of the artifact needed, the failed test or approval condition | One Waiting label can cover several blockers. |
| When the prerequisite was done and the ticket was ready to act on | Relevant logs received and accepted, environment ready, approval granted, test accepted, change window available | "Uploaded" can mean unsuitable material, and readiness isn't logged directly. |
| Who was responsible, and whether they could act | Accountable role, authority, access, skills, availability and competing commitments | An individual assignment isn't a team, queue, schedule or capacity record. |
| A reasonable response expectation | A policy or explicit commitment confirmed by the process owner, the calendar it applies to, exceptions and their rationale | Seven calendar days and reminder templates aren't verified standards. |
| What the next action actually was, and what was still blocking | Timestamped evidence of work, changes or approvals, not just status changes | Technical work happens inside Waiting, and the exit can lag behind the action or the restoration. |
| The complete communication chain | Comments, relevant calls and messages, linked development work and follow-on tickets, with the right access | The sampled text refers to communications off the platform and to new tickets. |
| An independent operational consequence | Verified restoration, how long users were affected, a missed commitment, repeat contact, a failed deployment or measured effort | Resolution or closure can just mean nonresponse or admin. |
| A credible comparison with acting earlier | Comparable episodes that were ready, a justified standard, or prospective evidence that earlier action was feasible with the same safeguards | Fastest peers and duration differences mix up case mix with legitimate dependencies. |

## How I'd label an episode

1. **Necessary dependency documented:** there's evidence of a specific blocking prerequisite. When it was completed, and how long it should take, may still be unknown, so don't label the whole interval necessary.
2. **Potentially addressable gap:** once a prerequisite looks satisfied, there's a plausible person and a feasible next action, but their availability, the expected timing, other blockers or the harm are still unverified.
3. **Verified avoidable operational delay:** someone authorized and available could have taken a specific earlier action after the relevant prerequisites were met; an applicable expectation was missed without a substantiated exception; and both a meaningful consequence and a credible earlier-action comparison are supported.
4. **Administrative status lag:** the operational action or recovery happened before the status was updated. Look into this separately, and don't count it as unrecovered service or as labor savings.
5. **Unknown / disputed:** the evidence is insufficient, masked, contradictory or incomplete. Keep this label instead of forcing one of the others.

Different parts of one episode can get different labels, so a ticket's whole duration shouldn't go to one reason. Each judgment should record evidence IDs, timestamps, the rationale, competing explanations and any disagreement, and say whether it came from a person or a model suggestion. This project has no stakeholder validation yet.

## Collecting the evidence, and when to pick a problem

The sample should be consecutive or probability-based, from real operations, with known inclusion rules. It should cover long and short waits, repeated and single waits, and the relevant projects and time periods. Hand-picked examples help explain mechanisms but can't estimate how big the burden is. The sample size should come from the prevalence, the uncertainty and the decision being made; an arbitrary small number won't deliver statistical significance.

The actual process owners need to confirm what each state means, who is responsible for what, and the exceptions. The proposed mechanism and any disagreements need independent review. Explanations of the form "this wait was necessary" need testing, and unresolved cases stay unknown. Before priority, project, reason or text is used as a predictor going forward, I'd need to check that it was really available at the time.

Then the decision rule:

- Pick **A** (Waiting is the problem) only if a recurring, materially harmful, controllable mechanism inside Waiting is shown for a defined population with reliable measurement.
- Pick **B** (a different problem) only if another problem has stronger evidence on those same criteria. A convenient transition in the data isn't enough.
- Otherwise stay with **C**, and either get better evidence or openly turn the project into a bounded observational study.

Process redesign, deterministic rules, traditional automation and AI only get evaluated after that point. Any later pilot or causal evaluation has to keep the necessary validation steps and operational safeguards. The current review can't support any savings or treatment-effect calculations.
