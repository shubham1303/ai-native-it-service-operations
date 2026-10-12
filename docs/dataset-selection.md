# Why I picked this dataset

Decided 2026-09-11.

I went with **Help Desk Tickets v3**. It's the only candidate that links a ticket's full lifecycle, its assignment changes and real customer conversations in one source, which is what you need to study a support process rather than just its outcomes. **BPI Challenge 2014** is the fallback if that ever stops working.

A note on the numbers below: counts marked **measured** come from files I downloaded and counted myself. **Publisher-reported** counts are the publisher's, and I haven't profiled them independently. The ranking is my judgment for this project, not a statistical score.

## The four candidates

| Rank | Candidate | Scale | Main strength | Main constraint |
|---|---|---|---|---|
| 1 | Help Desk Tickets v3 | **Measured:** 66,691 issues; 257,508 history rows; 90,963 assignee-cycle rows; 30,104 utterances for 360 issues | Linked lifecycle, assignment changes, and real sampled conversations | Mixed work types; limited, masked text; gaps in historical coverage |
| 2 | BPI Challenge 2014 suite | **Measured:** 466,737 incident activity rows covering 46,616 IDs; the incident file has 46,606 distinct nonblank IDs | The broadest coverage of ITIL entities and support groups | No narrative ticket text in the incident/activity files I inspected; joins and raw-file artifacts need care |
| 3 | UCI Incident Management Process Enriched Event Log | **Publisher-reported:** 141,712 events, 24,918 incidents, 36 attributes | Rich incident attributes and ServiceNow audit history | Text deliberately removed; identical-looking rows may hide different changes |
| 4 | BPI Challenge 2013 incidents | **Measured:** 65,533 events, 7,554 cases | Clear event sequences with organizational and resource context | Fewer business attributes and no usable narrative descriptions |

## 1. Help Desk Tickets, version 3 (selected)

**Where it comes from.** A masked extract from a real production helpdesk, published by Mohammad Abdellatif on Mendeley under CC BY 4.0. The original database isn't public. The publisher provides issue, history, assignee-cycle, sampled message, appraisal and holiday files. [Dataset](https://data.mendeley.com/datasets/btm76zndnt/3). There's also a companion [research repository](https://github.com/mohammadabdellatif/toward-performance-appraisal-automation) describing the study the extract came from. Its software is GPL-licensed, separately from the dataset, and I haven't reused any of its code.

**What's in it.** Issues have 58 columns, including creation and resolution dates, priority, type, project, final assignee, contributors, resolution/status, comment counts, and derived state-duration and visit columns. History has the issue ID, change ID, changed field, new value, timestamp and change-group ID. Both status changes and individual-assignee changes are there. There's no support-group hierarchy. Twenty distinct status values appear in the history. I kept the raw data dictionary at `data/raw/helpdesk_v3/FEATURES.md`.

**Text and resolution.** The text subset I measured covers only 360 issues and 7,286 comment IDs, with messages split into utterances. There's no general description field covering all issues. Masking strips out code, SQL, logs and many technical details. Resolution labels include Done, Won't Do, Duplicate and Cannot Reproduce. Those are outcome categories, not verified technical fixes.

**For process mining: high, once validated.** I can rebuild status changes and assignment episodes, look at rework, and compare paths across cohorts. Tied timestamps, missing initial history and the mix of issue types have to be dealt with first. How long someone owned a ticket can't be treated as how long they worked on it.

**For AI experiments: promising, with limits.** Structured process prediction and prioritizing what to review can use a broad cohort. If discovery justified it, a later communication-assistance experiment could use the small linked text subset, split by issue and time, never by utterance. The staff appraisal scores in the dataset don't label correct routing or safe fixes. And with scripts masked, there's nothing to evaluate executable technical fixes against.

**Access and fit.** The public files downloaded without credentials and matched the publisher's SHA-256 hashes. It's a strong fit for business systems analysis, because the relationships, data defects, workflow behavior and a possible communication layer can all be studied together. It's a software support operation, not necessarily an internal employee IT desk, so it can't support claims about enterprise IT performance in general.

## 2. BPI Challenge 2014 (strongest alternative)

**Where it comes from.** Anonymized HP Service Manager extracts from Rabobank Group ICT, attributed to Boudewijn van Dongen. The collection links interactions, incidents, changes and incident activities. [Publisher description](https://research.tue.nl/en/datasets/bpi-challenge-2014-activity-log-for-incidents/), [activity data](https://figshare.com/articles/dataset/BPI_Challenge_2014_Activity_log_for_incidents/12706424), [incident data](https://doi.org/10.4121/uuid:3cfa2260-f5c5-44be-afe1-b70d35288d6d).

**What's in it (measured).** Incident activity has a timestamp, activity type and number, assignment group, knowledge-document number and interaction ID. Incident details include priority, impact, urgency, category, reassignment count, opening/reopening/resolution/closure times, closure code, related-change fields, configuration-item classifications, and a field labeled Handle Time (Hours), whose meaning I'd still need to validate.

**Scale and data caveats.** The activity file has 466,737 rows and 46,616 IDs. The raw incident CSV parses to 46,809 rows with trailing unnamed columns, but has only 46,606 distinct nonblank incident IDs, so raw rows aren't the same as incidents. The differences between files need checking for orphans and duplicates. I identified the interaction and change files but didn't download or count them in this milestone, so I'm not giving counts for them.

**What it would be good for.** Very good for group handoffs, process variants, and hypotheses about changes. Structured prediction could be compared with rules. There's no text in the files I inspected to support narrative retrieval or recommending technical resolutions. Knowledge-document IDs don't come with the documents themselves. And linking incidents to changes can't, on its own, show that a release caused anything.

**License and access.** The repository metadata says **4TU General Terms of Use**, not CC BY. When some older 4TU links failed, the metadata and files were still reachable through the repository's Figshare API and download service. Attribution should be kept, and the exact terms checked before redistributing anything publicly. I ranked it on operational fit, not on a reading of the license.

**Why it came second.** It would be the better choice if discovery needed support-group analysis or connected change management. But the selected dataset bridges observed process and actual communication more broadly, and choosing BPI 2014 would have narrowed the text-based experiments I could run.

## 3. UCI enriched incident event log

**Where it comes from.** Real anonymized ServiceNow audit records, enriched from the underlying relational database. The publisher reports 141,712 rows, 24,918 incidents and 36 attributes. Fields include state, assignment group and person, priority/impact/urgency, categories, reassignment and reopen counters, an SLA flag, several timestamps and resolution fields. Text was left out on purpose. The CSV is public under CC BY 4.0. [UCI source and dictionary](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log).

**My assessment.** A strong candidate for structured analysis: elapsed resolution time, assignment behavior, reopening, and the SLA label. Snapshot ordering, what the counters mean and what the SLA flag means would all need validating. Repeated rows aren't automatically duplicates, because attributes that were left out may have changed. Final counters and closure fields would leak the answer if treated as intake inputs. It's good for comparing structured prediction with deterministic rules, and poor for testing natural-language resolution advice. It ranks below the two linked multi-table sources because they suit a systems-analysis project better, not because it's easier or harder to work with. I didn't verify its file counts myself.

## 4. BPI Challenge 2013 incidents

**Where it comes from.** Ward Steeman's Volvo IT incident-management log. [Repository record](https://figshare.com/articles/dataset/BPI_Challenge_2013_incidents/12693914/1). It's a public compressed XES file, and the repository lists the 4TU General Terms of Use.

**What's in it (measured).** 7,554 cases and 65,533 events. Event attributes include activity name, lifecycle transition, timestamp, impact, group, resource, role, organization/country and product. I didn't find separate priority or category fields, or narrative ticket descriptions, in the schema I inspected. Impact isn't the same as priority, and product isn't the same as incident category.

**My assessment.** Strong for reconstructing handoffs and lifecycles, delay patterns, and next-event or remaining-time experiments. The lifecycle endpoints need interpreting before anything can be labeled as resolved. It gives less context for a workflow intervention someone could act on, and little support for text-based experiments. It would work as a later robustness check on the process methods, but mixing its records with those of unrelated organizations wouldn't produce a coherent business system.

## The reasoning, and its limits

I chose Help Desk Tickets v3 for discovery because it combines a sizeable operational history, relational structure, multiple process paths, and real linked communications. The initial profile backed up using it, with the condition that the cohort had to be validated. The text sample is too small for broad claims about LLM performance. Having text is an option, not a reason to use AI.

None of the candidates has real post-intervention outcomes or thorough labels for which actions are safe. Historical paths describe what happened; they don't prove what the best next action would have been. Any intervention I eventually propose has to beat a relevant non-AI baseline and come with a human-review policy. I won't use synthetic text to invent the original problem or to pad the evaluation sample.

I'd revisit the choice if a defensible support cohort couldn't be rebuilt from this data, with BPI 2014 as the preferred fallback. Unattributed ticket dumps and synthetic helpdesk corpora don't meet the requirement that the primary data be authentic.
