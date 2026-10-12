# When each field becomes available

No feature set or AI intervention has been selected. This table records when each field is actually known, so that data recorded after the fact doesn't get used by accident as if it were available earlier.

| Field family | Earliest defensible availability | Policy |
|---|---|---|
| Issue ID, project-local number | Record exists | Join/audit only; exclude identity memorization as default |
| Recorded creation timestamp | Creation | Permitted for event-relative elapsed time once timezone is parsed |
| Type, priority, project, reporter | Only export state confirmed by this extract | Use for descriptive cohorts; intake-time stability requires evidence before prediction |
| Status and assignee history | Each update's created timestamp | Prefix-only input. A future update cannot characterize an earlier decision |
| First status/assignee | First observed update | Never backfill across the unobserved creation-to-update gap |
| Final assignee/status/resolution | Export/end-state observation | Exclude from intake predictors; candidate retrospective labels need definition |
| Resolution date, ended, last change | Outcome/latest observation | Exclude when future relative to decision; never use known final duration as predictor |
| wf_*, wfe_*, processing_steps | Computed over full supplied timeline | Exclude; recompute prefix aggregates from eligible events if justified |
| Total comments/contributors | Full-history summary | Exclude; prefix count from actual available events only |
| Utterance and comment metadata | Comment created timestamp | Only messages available by decision cutoff, with after-endpoint exceptions quarantined |
| author_role | Publisher retrospective mapping | Validate mapping against prefix ownership before prospective use |
| Appraisal ratings/notes | Original study review | Not prediction input or safe-action truth |
| Country holiday table | Publisher-derived calendar | Optional contextual calendar only; no inferred working hours |

Evaluation units must be independent issues. Do not random-split events, snapshots, comments or utterances. A temporal split also needs label-availability checks: a training issue whose outcome occurred after the training cutoff cannot supply that outcome as if it were known earlier. Fit imputers, encoders, thresholds and retrieval indexes on training data only. Keep synthetic API scenarios separate from all historical labels and metrics.
