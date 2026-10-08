-- Aggregate every child stream BEFORE joining to cases, preventing fan-out inflation.
WITH status AS (
 SELECT issueid,SUM(duration_seconds) observed_status_seconds,
 SUM(CASE WHEN value='waiting' THEN duration_seconds ELSE 0 END) waiting_seconds,
 SUM(CASE WHEN value='resolved' THEN duration_seconds ELSE 0 END) resolved_seconds,
 SUM(CASE WHEN value='resolved_under_monitoring' THEN duration_seconds ELSE 0 END) monitoring_seconds,
 SUM(CASE WHEN value='pending_deployment' THEN duration_seconds ELSE 0 END) deployment_seconds,
 SUM(CASE WHEN value='in_progress' THEN duration_seconds ELSE 0 END) in_progress_seconds,
 SUM(CASE WHEN value='validation' THEN duration_seconds ELSE 0 END) validation_seconds,
 SUM(value='waiting') waiting_entries,
 SUM(value='validation') validation_entries
 FROM observed_intervals WHERE field='status' GROUP BY issueid
), paths AS (
 SELECT issueid,SUM(previous_value='validation' AND value='in_progress') validation_returns,
 SUM(previous_value='waiting' AND value='in_progress') waiting_returns,
 SUM(value='reopened' AND previous_ts IS NOT NULL) reopen_entries,
 SUM(previous_ts IS NOT NULL) status_changes
 FROM change_events WHERE field='status' GROUP BY issueid
)
SELECT i.id,i.issue_created,i.issue_created_ts,i.issue_resolution_date_ts,
 i.ended_ts,i.issue_type,i.issue_proj,i.issue_priority,i.issue_status,i.is_external_project,
 c.external_ticket,c.broad_service,c.primary_population,c.status_eligible,c.assignment_eligible,
 q.status_rows,q.assignee_rows,q.events_before_creation,q.events_after_endpoint,
 q.status_conflict,q.assignee_conflict,q.invalid_event_times,q.invalid_bounds,q.final_status_mismatch,
 q.initial_status_gap_seconds,q.invalid_resolution_bounds,
 m.recorded_resolution_seconds,m.first_resolved_state_seconds,
 m.observed_named_handoffs,m.observed_assignment_blank_transitions,
 s.observed_status_seconds,s.waiting_seconds,s.resolved_seconds,s.monitoring_seconds,s.deployment_seconds,
 s.in_progress_seconds,s.validation_seconds,s.waiting_entries,s.validation_entries,
 p.validation_returns,p.waiting_returns,p.reopen_entries,p.status_changes
FROM stg_issues i JOIN cohort_membership c ON c.id=i.id JOIN issue_quality q ON q.id=i.id
JOIN case_observed_measures m ON m.id=i.id
LEFT JOIN status s ON s.issueid=i.id LEFT JOIN paths p ON p.issueid=i.id;
