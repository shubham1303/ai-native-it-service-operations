-- SQLite analytical layer. UTC epoch seconds are parsed upstream without rounding.
-- Stage tables preserve source row, original keys and source values.
CREATE TABLE analysis_settings AS
SELECT unixepoch('2019-01-01T00:00:00Z') AS primary_start_ts;
CREATE INDEX IF NOT EXISTS hist_issue ON stg_history(issueid);
CREATE INDEX IF NOT EXISTS issue_id ON stg_issues(id);
CREATE INDEX IF NOT EXISTS snap_issue ON stg_snapshots(id);

CREATE TABLE event_conflicts AS
SELECT issueid, field, created_ts, COUNT(*) AS source_rows,
       COUNT(DISTINCT value) AS different_values
FROM stg_history GROUP BY issueid, field, created_ts
HAVING COUNT(DISTINCT value)>1 OR created_ts IS NULL;
CREATE INDEX conflicts_issue ON event_conflicts(issueid,field);

-- Equivalent values at the same instant are one observation; source multiplicity retained.
CREATE TABLE observed_events AS
SELECT h.issueid,h.field,h.created_ts,h.value,MIN(h.source_row) AS first_source_row,
       GROUP_CONCAT(h.id) AS source_event_ids,COUNT(*) AS source_event_count
FROM stg_history h
WHERE NOT EXISTS (SELECT 1 FROM event_conflicts c
                  WHERE c.issueid=h.issueid AND c.field=h.field)
GROUP BY h.issueid,h.field,h.created_ts,h.value;
CREATE INDEX obs_issue ON observed_events(issueid,field,created_ts);

CREATE TABLE event_sequence AS
SELECT *,LAG(value) OVER(PARTITION BY issueid,field ORDER BY created_ts) AS previous_value,
 LAG(created_ts) OVER(PARTITION BY issueid,field ORDER BY created_ts) AS previous_ts
FROM observed_events;

CREATE TABLE change_events AS
SELECT * FROM event_sequence WHERE previous_ts IS NULL OR value<>previous_value;
CREATE INDEX changes_issue ON change_events(issueid,field);

CREATE TABLE observed_intervals AS
WITH ordered AS (
 SELECT *, LEAD(created_ts) OVER(PARTITION BY issueid,field ORDER BY created_ts) AS next_ts
 FROM change_events
), bounded AS (
 SELECT e.*,i.issue_created_ts,i.ended_ts,
 MIN(COALESCE(e.next_ts,i.ended_ts),i.ended_ts) AS end_ts
 FROM ordered e JOIN stg_issues i ON e.issueid=i.id
)
SELECT *,end_ts-created_ts AS duration_seconds
FROM bounded WHERE created_ts>=issue_created_ts AND created_ts<=ended_ts
 AND end_ts>=created_ts;
CREATE INDEX intervals_issue ON observed_intervals(issueid,field);

CREATE TABLE issue_quality AS
WITH hist AS (
 SELECT h.issueid,COUNT(*) AS history_rows,
 SUM(h.field='status') AS status_rows,SUM(h.field='assignee') AS assignee_rows,
 MIN(h.created_ts) AS first_history_ts,MAX(h.created_ts) AS last_history_ts,
 SUM(h.created_ts<i.issue_created_ts) AS events_before_creation,
 SUM(h.created_ts>i.ended_ts) AS events_after_endpoint,
 SUM(h.created_ts IS NULL) AS invalid_event_times
 FROM stg_history h JOIN stg_issues i ON i.id=h.issueid GROUP BY h.issueid
), last_status AS (
 SELECT issueid,value,ROW_NUMBER() OVER(PARTITION BY issueid ORDER BY created_ts DESC) rn
 FROM observed_events WHERE field='status'
), first_status AS (
 SELECT issueid,value,created_ts,ROW_NUMBER() OVER(PARTITION BY issueid ORDER BY created_ts) rn
 FROM observed_events WHERE field='status'
)
SELECT i.id,COALESCE(h.history_rows,0) history_rows,COALESCE(h.status_rows,0) status_rows,
 COALESCE(h.assignee_rows,0) assignee_rows,h.first_history_ts,h.last_history_ts,
 COALESCE(h.events_before_creation,0) events_before_creation,
 COALESCE(h.events_after_endpoint,0) events_after_endpoint,
 COALESCE(h.invalid_event_times,0) invalid_event_times,
 EXISTS(SELECT 1 FROM event_conflicts c WHERE c.issueid=i.id AND c.field='status') status_conflict,
 EXISTS(SELECT 1 FROM event_conflicts c WHERE c.issueid=i.id AND c.field='assignee') assignee_conflict,
 ls.value last_observed_status,fs.value first_observed_status,
 fs.created_ts-i.issue_created_ts initial_status_gap_seconds,
 CASE WHEN ls.value IS NULL THEN NULL ELSE ls.value<>i.issue_status END final_status_mismatch,
 CASE WHEN i.issue_created_ts IS NULL OR i.ended_ts IS NULL OR i.ended_ts<i.issue_created_ts THEN 1 ELSE 0 END invalid_bounds,
 CASE WHEN i.issue_resolution_date_ts<i.issue_created_ts OR i.issue_resolution_date_ts>i.ended_ts THEN 1 ELSE 0 END invalid_resolution_bounds
FROM stg_issues i LEFT JOIN hist h ON i.id=h.issueid
LEFT JOIN last_status ls ON ls.issueid=i.id AND ls.rn=1
LEFT JOIN first_status fs ON fs.issueid=i.id AND fs.rn=1;
CREATE INDEX quality_id ON issue_quality(id);

CREATE TABLE cohort_membership AS
SELECT i.id,
 CASE WHEN i.is_external_project=1 AND i.issue_type='Ticket' THEN 1 ELSE 0 END external_ticket,
 CASE WHEN i.is_external_project=1 AND i.issue_type IN ('Ticket','Service','HD Service') THEN 1 ELSE 0 END broad_service,
 CASE WHEN i.is_external_project=1 AND i.issue_type='Ticket'
       AND i.issue_created_ts>=(SELECT primary_start_ts FROM analysis_settings) THEN 1 ELSE 0 END primary_population,
 CASE WHEN i.is_external_project=1 AND i.issue_type='Ticket' AND i.issue_created_ts>=(SELECT primary_start_ts FROM analysis_settings)
       AND q.status_rows>0 AND q.status_conflict=0 AND q.invalid_event_times=0
       AND q.events_before_creation=0 AND q.events_after_endpoint=0
       AND q.invalid_bounds=0 AND q.final_status_mismatch=0 THEN 1 ELSE 0 END status_eligible,
 CASE WHEN i.is_external_project=1 AND i.issue_type='Ticket' AND i.issue_created_ts>=(SELECT primary_start_ts FROM analysis_settings)
       AND q.assignee_rows>0 AND q.assignee_conflict=0 AND q.invalid_event_times=0
       AND q.events_before_creation=0 AND q.events_after_endpoint=0 AND q.invalid_bounds=0
       THEN 1 ELSE 0 END assignment_eligible
FROM stg_issues i JOIN issue_quality q ON i.id=q.id;

CREATE TABLE status_transitions AS
SELECT e.* FROM change_events e JOIN cohort_membership c ON e.issueid=c.id
WHERE e.field='status' AND e.previous_ts IS NOT NULL AND c.status_eligible=1;

CREATE TABLE case_observed_measures AS
SELECT i.id,
 i.issue_resolution_date_ts-i.issue_created_ts AS recorded_resolution_seconds,
 i.ended_ts-i.issue_created_ts AS source_endpoint_seconds,
 (SELECT MIN(created_ts)-i.issue_created_ts FROM change_events e
  WHERE e.issueid=i.id AND field='status' AND value='resolved') AS first_resolved_state_seconds,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=i.id AND field='status'
  AND value='reopened' AND previous_ts IS NOT NULL) AS observed_reopen_entries,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=i.id AND field='assignee'
  AND previous_ts IS NOT NULL AND value<>'' AND previous_value<>'') AS observed_named_handoffs,
 (SELECT COUNT(*) FROM change_events e WHERE e.issueid=i.id AND field='assignee'
  AND previous_ts IS NOT NULL AND (value='' OR previous_value='')) AS observed_assignment_blank_transitions,
 (SELECT SUM(duration_seconds) FROM observed_intervals e WHERE e.issueid=i.id
  AND field='status' AND value='waiting') AS observed_waiting_seconds
FROM stg_issues i;

-- Consumer-facing views enforce metric-specific eligibility. Diagnostic tables retain all cases.
CREATE VIEW analysis_status_intervals AS
SELECT e.* FROM observed_intervals e JOIN cohort_membership c ON c.id=e.issueid
WHERE e.field='status' AND c.status_eligible=1;

CREATE VIEW analysis_assignment_intervals AS
SELECT e.* FROM observed_intervals e JOIN cohort_membership c ON c.id=e.issueid
WHERE e.field='assignee' AND c.assignment_eligible=1;

CREATE VIEW analysis_case_measures AS
SELECT m.id,c.primary_population,c.status_eligible,c.assignment_eligible,
 CASE WHEN c.primary_population=1 AND q.invalid_resolution_bounds=0
      THEN m.recorded_resolution_seconds END recorded_resolution_seconds,
 CASE WHEN c.status_eligible=1 THEN m.first_resolved_state_seconds END first_resolved_state_seconds,
 CASE WHEN c.status_eligible=1 THEN m.observed_reopen_entries END observed_reopen_entries,
 CASE WHEN c.assignment_eligible=1 THEN m.observed_named_handoffs END observed_named_handoffs,
 CASE WHEN c.assignment_eligible=1 THEN m.observed_assignment_blank_transitions END observed_assignment_blank_transitions,
 CASE WHEN c.status_eligible=1 THEN COALESCE(m.observed_waiting_seconds,0) END observed_waiting_seconds
FROM case_observed_measures m JOIN cohort_membership c ON c.id=m.id JOIN issue_quality q ON q.id=m.id;
