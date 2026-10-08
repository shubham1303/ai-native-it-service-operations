# Dataset selection

Decision date: 2026-09-11. Counts marked **measured** come from the downloaded files. **Publisher-reported** counts have not been independently profiled here. Rankings are project judgments, not statistical scores.

## Ranking

| Rank | Candidate | Scale | Main strength | Main constraint |
|---|---|---|---|---|
| 1 | Help Desk Tickets v3 | **Measured:** 66,691 issues; 257,508 history rows; 90,963 assignee-cycle rows; 30,104 utterances for 360 issues | Linked lifecycle, assignment changes, and authentic sampled conversations | Mixed work types; limited, masked text; historical coverage gaps |
| 2 | BPI Challenge 2014 suite | **Measured:** 466,737 incident activity rows covering 46,616 IDs; incident file contains 46,606 distinct nonblank IDs | Strongest breadth across ITIL entities and support groups | No narrative ticket corpus in inspected incident/activity files; joins and raw-file artifacts require care |
| 3 | UCI Incident Management Process Enriched Event Log | **Publisher-reported:** 141,712 events, 24,918 incidents, 36 attributes | Rich incident attributes and ServiceNow audit history | Text deliberately removed; identical observed rows may represent distinct hidden changes |
| 4 | BPI Challenge 2013 incidents | **Measured:** 65,533 events, 7,554 cases | Clear event sequences with organizational/resource context | Narrower business attributes and no usable narrative descriptions |

## 1. Help Desk Tickets, version 3 — selected

**Source and authenticity.** Mohammad Abdellatif’s masked production helpdesk extract, published on Mendeley under CC BY 4.0. The original database is not public. The publisher supplies issue, history, assignee-cycle, sampled message, appraisal, and holiday files. [Dataset](https://data.mendeley.com/datasets/btm76zndnt/3). Its companion [research repository](https://github.com/mohammadabdellatif/toward-performance-appraisal-automation) documents the extraction study; its GPL software license is separate from the dataset license. We have not reused its implementation.

**Measured schema and lifecycle.** Issues have 58 columns, including creation/resolution dates, priority, type, project, final assignee, contributors, resolution/status, comment counts, and derived state-duration/visit columns. History has issue ID, change ID, changed field, new value, timestamp, and change-group ID. Both status and individual-assignee changes are present. Support-group hierarchy is absent. Twenty distinct historical status values occur. The raw dictionary is preserved locally in `data/raw/helpdesk_v3/FEATURES.md`.

**Text and resolution.** The measured text subset covers only 360 issues and 7,286 comment IDs. Messages are split into utterances. There is no general description field for all issues. Masking removes code, SQL, logs, and many technical details. Resolution labels include Done, Won't Do, Duplicate, and Cannot Reproduce. These are outcome categories, not verified technical fixes.

**Process-mining potential — high after validation.** We can reconstruct status changes and assignment episodes, examine rework, and compare observed paths across cohorts. Tied timestamps, missing initial history, and different issue types must be addressed first. Ownership duration cannot be treated as labor time.

**AI experimentation potential — promising but constrained.** Structured process prediction and review prioritization can use a broad cohort. A later communication-assistance experiment could use the small linked text subset, if discovery justifies it. Split by issue and time, never by utterance. Existing staff-appraisal scores do not label correct routing or safe remediation. No basis exists for evaluating executable technical fixes from masked scripts.

**Accessibility and suitability.** Public files downloaded without credentials and matched publisher SHA-256 hashes. Strong fit for business systems analysis because relationships, data defects, workflow behavior, and a potential communication layer can be studied together. The system represented is software support, not necessarily an internal employee IT desk. It is unsuitable for claiming universal enterprise IT performance.

## 2. BPI Challenge 2014 — strongest alternative

**Source/authenticity.** Rabobank Group ICT’s anonymized HP Service Manager extracts, attributed to Boudewijn van Dongen. The published collection links interactions, incidents, changes, and incident activities. [Publisher description](https://research.tue.nl/en/datasets/bpi-challenge-2014-activity-log-for-incidents/), [activity data](https://figshare.com/articles/dataset/BPI_Challenge_2014_Activity_log_for_incidents/12706424), [incident data](https://doi.org/10.4121/uuid:3cfa2260-f5c5-44be-afe1-b70d35288d6d).

**Measured fields.** Incident activity provides timestamp, activity type/number, assignment group, knowledge-document number, and interaction ID. Incident details include priority, impact, urgency, category, reassignment count, opening/reopening/resolution/closure times, closure code, related-change fields, configuration-item classifications, and a field labeled Handle Time (Hours). Its measurement semantics still need validation.

**Scale and data caveats.** The activity file contains 466,737 rows and 46,616 IDs. The raw incident CSV parses to 46,809 rows with trailing unnamed columns, but only 46,606 distinct nonblank incident IDs. Raw rows are not equivalent to incidents. Cross-file differences need orphan and duplicate investigation. Interaction/change files were identified but not downloaded or counted in this milestone; no unverified counts are supplied for them.

**Evaluation suitability.** Excellent for group handoffs, process variants, and change-related operational hypotheses. Structured prediction can be compared with rules. Narrative retrieval and technical resolution recommendation lack supporting text in the inspected files. Knowledge-document IDs do not supply document contents. Change associations cannot establish causal release impact alone.

**License/access.** Repository metadata says **4TU General Terms of Use**, not CC BY. Metadata and files were accessible through the repository’s Figshare API/download service when some legacy 4TU links failed. Preserve attribution; inspect the exact terms before public redistribution. This ranking is based on operational fit, not a license interpretation.

**Why second.** Better fit if discovery requires support-group analysis or connected change management. The selected dataset offers a broader bridge between observed process and actual communication; choosing BPI 2014 would narrow the possible text-based experiments.

## 3. UCI enriched incident event log

**Source/authenticity.** Real anonymized ServiceNow audit records enriched from the underlying relational database. Publisher reports 141,712 rows, 24,918 incidents and 36 attributes. Fields include state, assignment group/person, priority/impact/urgency, categories, reassignment/reopen counters, SLA flag, multiple timestamps and resolution fields. Text was intentionally omitted. CSV is public under CC BY 4.0. [UCI source and dictionary](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log).

**Assessment.** Strong structured analysis candidate: elapsed resolution, assignment behavior, reopening and SLA-label analysis. Snapshot ordering, counter semantics, and SLA-flag meaning require validation. Repeated rows are not automatically duplicates because excluded attributes may have changed. Final counters and closure fields create prediction leakage if treated as intake inputs. Good for structured prediction versus deterministic rules; poor for testing natural-language resolution advice. It ranks below the two linked multi-table sources for this systems-analysis project, not because it is easier or harder. File counts were not independently verified.

## 4. BPI Challenge 2013 incidents

**Source/authenticity.** Ward Steeman’s Volvo IT incident-management log. [Repository record](https://figshare.com/articles/dataset/BPI_Challenge_2013_incidents/12693914/1). Public compressed XES; repository lists 4TU General Terms of Use.

**Measured content.** 7,554 cases and 65,533 events. Event attributes include activity name, lifecycle transition, timestamp, impact, group, resource, role, organization/country and product. No separate priority/category fields or narrative ticket descriptions were found in the inspected schema. Impact is not automatically priority, and product is not incident category.

**Assessment.** Strong for handoff and lifecycle reconstruction, delay patterns and next-event/remaining-time experiments. Lifecycle endpoints need interpretation before labeling resolution. Less context for actionable workflow intervention and little support for text-based experiments. Appropriate as a later process-method robustness check, but combining its records with unrelated organizations would not create a coherent business system.

## Selection reasoning and boundaries

Choose Help Desk Tickets v3 for discovery because it combines a sizeable operational history, relational structure, multiple paths, and authentic linked communications. The initial profile supports continued use but requires cohort validation. The text sample’s size prevents broad LLM-performance claims. Its presence is an option, not a justification for AI.

No candidate supplies real post-intervention outcomes or comprehensive labels for safe actions. Historical paths are descriptions of what happened, not proof of the optimal next action. Any eventual intervention must outperform a relevant non-AI baseline and have a human-review policy. Synthetic text will not be used to invent the original problem or inflate evaluation sample size.

Revisit selection if a defensible support cohort cannot be reconstructed. BPI 2014 is the preferred fallback. Unattributed ticket dumps and synthetic helpdesk corpora do not pass the primary-data authenticity requirement.
