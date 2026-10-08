-- The window spans ALL status changes before filtering to Waiting.
WITH seq AS (
 SELECT e.*,LEAD(value) OVER(PARTITION BY issueid ORDER BY created_ts) AS next_state
 FROM change_events e WHERE field='status'
), waits AS (
 SELECT a.issueid,a.created_ts,a.end_ts,a.duration_seconds,s.previous_value AS previous_state,
 s.next_state,s.source_event_ids,
 ROW_NUMBER() OVER(PARTITION BY a.issueid ORDER BY a.created_ts) AS episode_number,
 COUNT(*) OVER(PARTITION BY a.issueid) AS issue_wait_episodes,
 LAG(a.end_ts) OVER(PARTITION BY a.issueid ORDER BY a.created_ts) AS prior_wait_exit
 FROM analysis_status_intervals a JOIN seq s ON s.issueid=a.issueid AND s.created_ts=a.created_ts
 WHERE a.value='waiting'
)
SELECT w.*,i.issue_created_ts,i.ended_ts,i.issue_proj,i.issue_priority,i.issue_status,
 strftime('%Y',i.issue_created_ts,'unixepoch') AS creation_year,
 c.assignment_eligible,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='status'
   AND e.previous_value='validation' AND e.value='in_progress' AND e.created_ts<w.created_ts) prior_validation_returns,
 CASE WHEN c.assignment_eligible=1 THEN
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='assignee'
  AND e.previous_ts IS NOT NULL AND e.value<>'' AND e.previous_value<>'' AND e.created_ts<w.created_ts) END prior_named_handoffs,
 CASE WHEN c.assignment_eligible=1 THEN
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='assignee'
  AND e.previous_ts IS NOT NULL AND e.value<>'' AND e.previous_value<>''
  AND e.created_ts>=w.created_ts AND e.created_ts<w.end_ts) END during_named_handoffs,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='status'
  AND e.previous_value='validation' AND e.value='in_progress'
  AND e.created_ts>=w.prior_wait_exit AND e.created_ts<w.created_ts) gap_validation_returns,
 CASE WHEN c.assignment_eligible=1 THEN
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='assignee'
  AND e.previous_ts IS NOT NULL AND e.value<>'' AND e.previous_value<>''
  AND e.created_ts>=w.prior_wait_exit AND e.created_ts<w.created_ts) END gap_named_handoffs,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='status'
  AND e.value='reopened' AND e.created_ts>w.end_ts AND e.created_ts<=w.end_ts+2592000) reopen_within_30d,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=w.issueid AND e.field='status'
  AND e.previous_value='validation' AND e.value='in_progress'
  AND e.created_ts>w.end_ts AND e.created_ts<=w.end_ts+2592000) validation_return_within_30d
FROM waits w JOIN stg_issues i ON i.id=w.issueid JOIN cohort_membership c ON c.id=w.issueid;
