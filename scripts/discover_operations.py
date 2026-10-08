"""Milestone 3 descriptive discovery. Associations are not treatment effects."""
from pathlib import Path
import hashlib
import json
import sqlite3
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/milestone3'
DB=ROOT/'data/analytical/service_operations.sqlite'
SEED=20260911
BOOTSTRAPS=1000

def elapsed_summary(series):
    values=series.dropna()/86400
    return dict(eligible_cases=len(values),mean_days=float(values.mean()),median_days=float(values.median()),
                p90_days=float(values.quantile(.9)),p95_days=float(values.quantile(.95)))

def bootstrap_median_difference(a,b):
    """Exploratory case-resampling percentile interval, conditional on observed groups."""
    a=np.asarray(a.dropna(),dtype=float)/86400;b=np.asarray(b.dropna(),dtype=float)/86400
    if min(len(a),len(b))<20:return [None,None]
    rng=np.random.default_rng(SEED)
    result=np.array([np.median(rng.choice(a,len(a),replace=True))-np.median(rng.choice(b,len(b),replace=True))
                     for _ in range(BOOTSTRAPS)])
    return np.quantile(result,[.025,.975]).tolist()

def stratified_association(df,exposure):
    rows=[]
    for keys,group in df.dropna(subset=['recorded_resolution_seconds']).groupby(['year','issue_priority','issue_proj']):
        a=group.loc[group[exposure],'recorded_resolution_seconds']/86400
        b=group.loc[~group[exposure],'recorded_resolution_seconds']/86400
        if min(len(a),len(b))<5:continue
        rows.append(dict(year=int(keys[0]),priority=keys[1],project=keys[2],exposed=len(a),unexposed=len(b),
            median_difference_days=float(a.median()-b.median()),
            log_mean_difference=float(np.log1p(a).mean()-np.log1p(b).mean()),weight=min(len(a),len(b))))
    table=pd.DataFrame(rows)
    if not rows:return table,dict(strata=0)
    return table,dict(strata=len(table),overlap_cases=int((table.exposed+table.unexposed).sum()),
        positive_median_difference_strata=int(table.median_difference_days.gt(0).sum()),
        overlap_weighted_log_difference=float(np.average(table.log_mean_difference,weights=table.weight)),
        note='Descriptive within year/recorded priority/project association; no causal interpretation')

def project_bootstrap_difference(df,exposure,repetitions=500):
    """Resample entire masked projects; retains within-project dependence in each draw."""
    df=df.dropna(subset=['recorded_resolution_seconds'])
    groups=[(g[exposure].to_numpy(),g.recorded_resolution_seconds.to_numpy()/86400)
            for _,g in df.groupby('issue_proj')]
    rng=np.random.default_rng(SEED);differences=[]
    for _ in range(repetitions):
        selected=[groups[n] for n in rng.integers(0,len(groups),len(groups))]
        flag=np.concatenate([x[0] for x in selected]);days=np.concatenate([x[1] for x in selected])
        if flag.any() and (~flag).any():differences.append(np.median(days[flag])-np.median(days[~flag]))
    return dict(projects=len(groups),replicates=len(differences),
        percentile_95_interval_days=np.quantile(differences,[.025,.975]).tolist(),
        note='Exploratory project-cluster resampling; not causal and no protection from shared dependencies across projects')

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
    cases=pd.read_sql((ROOT/'sql/discovery_cases.sql').read_text(),con)
    assert cases.id.is_unique and len(cases)==66691
    cases['year']=pd.to_datetime(cases.issue_created,utc=True,format='mixed').dt.year
    primary=cases[cases.primary_population.eq(1)].copy()
    status=primary[primary.status_eligible.eq(1)].copy()
    assignment=primary[primary.assignment_eligible.eq(1)].copy()
    joint=status[status.assignment_eligible.eq(1)].copy()
    # Candidate flags are retrospective diagnostics; no predictive input eligibility implied.
    for frame in [cases,primary,status,assignment,joint]:
        frame['any_waiting']=frame.waiting_entries.fillna(0).gt(0)
        frame['repeat_waiting']=frame.waiting_entries.fillna(0).ge(2)
        frame['long_waiting']=frame.waiting_seconds.fillna(0).ge(7*86400)
        frame['validation_return']=frame.validation_returns.fillna(0).gt(0)
        frame['reopened']=frame.reopen_entries.fillna(0).gt(0)
        frame['multiple_handoffs']=frame.observed_named_handoffs.ge(2)
        frame['any_handoff']=frame.observed_named_handoffs.ge(1)
        frame['resolved_holding']=frame.resolved_seconds.fillna(0).ge(7*86400)
    summary={'scope':'Observed historical descriptive analysis; no causal or AI impact estimates',
        'seed':SEED,'bootstrap_replicates':BOOTSTRAPS,'primary_cases':len(primary),
        'status_cases':len(status),'assignment_cases':len(assignment),'joint_cases':len(joint),
        'recorded_resolution':elapsed_summary(primary.recorded_resolution_seconds),
        'missing_resolution':int(primary.recorded_resolution_seconds.isna().sum()),
        'closed_with_missing_resolution':int((primary.issue_status.eq('closed')&primary.recorded_resolution_seconds.isna()).sum()),
        'source_sql_sha256':hashlib.sha256((ROOT/'sql/discovery_cases.sql').read_bytes()).hexdigest(),
        'pipeline_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    annual=[]
    for year,frame in primary.groupby('year'):
        annual.append(dict(year=int(year),cases=len(frame),missing_resolution=int(frame.recorded_resolution_seconds.isna().sum()),
            status_excluded=int(frame.status_eligible.eq(0).sum()),assignment_excluded=int(frame.assignment_eligible.eq(0).sum()),
            **elapsed_summary(frame.recorded_resolution_seconds)))
    pd.DataFrame(annual).to_csv(OUT/'baseline-by-year.csv',index=False)
    intervals=pd.read_sql('SELECT issueid,value,duration_seconds FROM analysis_status_intervals',con)
    state_table=intervals.groupby('value').agg(observed_seconds=('duration_seconds','sum'),
        intervals=('value','size'),affected_cases=('issueid','nunique'))
    state_table['calendar_days']=state_table.observed_seconds/86400
    state_table['share_observed_time']=state_table.observed_seconds/state_table.observed_seconds.sum()
    state_table.sort_values('observed_seconds',ascending=False).to_csv(OUT/'state-time-distribution.csv')
    summary['observed_status_calendar_days']=float(state_table.calendar_days.sum())
    summary['observed_waiting_calendar_days']=float(state_table.loc['waiting','calendar_days'])
    summary['waiting_share_excluding_closed_done_cancelled']=float(state_table.loc['waiting','observed_seconds']/state_table.loc[~state_table.index.isin(['closed','done','cancelled']),'observed_seconds'].sum())
    positive_wait_counts=intervals[intervals.value.eq('waiting')&intervals.duration_seconds.gt(0)].groupby('issueid').size()
    summary['repeated_positive_duration_wait_cases']=int(positive_wait_counts.ge(2).sum())
    pd.DataFrame([dict(threshold_calendar_days=days,affected_cases=int(status.waiting_seconds.ge(days*86400).sum()),
        case_share=float(status.waiting_seconds.ge(days*86400).mean())) for days in [3,7,14,30]]).to_csv(OUT/'waiting-threshold-sensitivity.csv',index=False)
    # Descriptive candidates; long-duration flags partly share the elapsed-time outcome by construction.
    flags=['any_waiting','repeat_waiting','long_waiting','validation_return','reopened','multiple_handoffs','resolved_holding']
    findings=[];strata_summary={}
    for flag in flags:
        frame=joint if flag=='multiple_handoffs' else status
        a=frame[frame[flag]];b=frame[~frame[flag]]
        findings.append(dict(candidate=flag,denominator=len(frame),affected_cases=len(a),share=len(a)/len(frame),
            exposed_resolved_cases=int(a.recorded_resolution_seconds.notna().sum()),
            unexposed_resolved_cases=int(b.recorded_resolution_seconds.notna().sum()),
            exposed_median_recorded_days=float(a.recorded_resolution_seconds.median()/86400),
            unexposed_median_recorded_days=float(b.recorded_resolution_seconds.median()/86400),
            exposed_p90_recorded_days=float(a.recorded_resolution_seconds.quantile(.9)/86400)))
        if flag in ['repeat_waiting','validation_return','reopened','multiple_handoffs']:
            table,stat=stratified_association(frame,flag)
            table.to_csv(OUT/f'{flag}-within-strata.csv',index=False)
            stat['case_bootstrap_median_difference_95_interval_days']=bootstrap_median_difference(a.recorded_resolution_seconds,b.recorded_resolution_seconds)
            stat['project_cluster_sensitivity']=project_bootstrap_difference(frame,flag)
            strata_summary[flag]=stat
    pd.DataFrame(findings).to_csv(OUT/'candidate-observations.csv',index=False)
    summary['stratified_associations']=strata_summary
    contributions=[]
    for flag in flags:
        frame=joint if flag=='multiple_handoffs' else status
        affected=frame[frame[flag]]
        contributions.append(dict(candidate=flag,cases=len(affected),
            observed_status_time_share=float(affected.observed_status_seconds.sum()/frame.observed_status_seconds.sum()),
            observed_waiting_time_share=float(affected.waiting_seconds.sum()/frame.waiting_seconds.sum())))
    pd.DataFrame(contributions).to_csv(OUT/'candidate-time-contributions.csv',index=False)
    summary['long_and_repeat_waiting']=dict(intersection=int((status.long_waiting&status.repeat_waiting).sum()),
        union=int((status.long_waiting|status.repeat_waiting).sum()))
    # Validation repeatability by year and recorded priority, rather than a single pooled association.
    segments=[]
    for segment in ['year','issue_priority']:
        for value,frame in status.groupby(segment):
            segments.append(dict(segment=segment,value=str(value),cases=len(frame),
                any_waiting=int(frame.any_waiting.sum()),repeat_waiting=int(frame.repeat_waiting.sum()),
                long_waiting=int(frame.long_waiting.sum()),validation_return=int(frame.validation_return.sum()),
                reopened=int(frame.reopened.sum()),resolved_holding=int(frame.resolved_holding.sum()),
                waiting_share_observed_time=float(frame.waiting_seconds.sum()/frame.observed_status_seconds.sum())))
    pd.DataFrame(segments).to_csv(OUT/'candidate-segments.csv',index=False)
    # Broader/window sensitivity uses the same quality gate, not the primary-membership flag.
    quality=cases.status_rows.gt(0)&cases.status_conflict.eq(0)&cases.invalid_event_times.eq(0)&cases.events_before_creation.eq(0)&cases.events_after_endpoint.eq(0)&cases.invalid_bounds.eq(0)&cases.final_status_mismatch.eq(0)
    sensitivity=[]
    for start in [2016,2017,2018,2019,2020]:
        for name,scope in [('external_ticket',cases.external_ticket.eq(1)),('broad_service',cases.broad_service.eq(1))]:
            f=cases[quality&scope&cases.year.ge(start)]
            sensitivity.append(dict(start_year=start,scope=name,status_cases=len(f),any_waiting=int(f.any_waiting.sum()),
                repeat_waiting=int(f.repeat_waiting.sum()),validation_return=int(f.validation_return.sum()),
                reopened=int(f.reopened.sum()),waiting_time_share=float(f.waiting_seconds.sum()/f.observed_status_seconds.sum())))
    pd.DataFrame(sensitivity).to_csv(OUT/'discovery-sensitivity.csv',index=False)
    # Fixed exposure window: clip to first 30 days; eligible only if source endpoint reaches day 30
    # or has a recorded resolution and final Closed state within day 30. This is a selected check.
    window=status[(status.ended_ts-status.issue_created_ts).ge(30*86400)|
        (status.recorded_resolution_seconds.le(30*86400)&status.issue_status.eq('closed'))].copy()
    time_intervals=pd.read_sql('SELECT issueid,value,created_ts,end_ts FROM analysis_status_intervals',con)
    bounded=time_intervals.merge(window[['id','issue_created_ts']],left_on='issueid',right_on='id')
    bounded['seconds_30d']=(np.minimum(bounded.end_ts,bounded.issue_created_ts+30*86400)-bounded.created_ts).clip(lower=0)
    summary['fixed_30day_selected_sensitivity']=dict(cases=len(window),
        waiting_share=float(bounded.loc[bounded.value.eq('waiting'),'seconds_30d'].sum()/bounded.seconds_30d.sum()),
        note='Selected follow-up check; does not establish complete capture or remove outcome selection')
    first_resolved=status.dropna(subset=['first_resolved_state_seconds']).copy()
    first_resolved['resolved_ts']=first_resolved.issue_created_ts+first_resolved.first_resolved_state_seconds
    before=time_intervals.merge(first_resolved[['id','resolved_ts']],left_on='issueid',right_on='id')
    before['seconds']=(np.minimum(before.end_ts,before.resolved_ts)-before.created_ts).clip(lower=0)
    summary['before_first_resolved_sensitivity']=dict(cases=len(first_resolved),
        waiting_share=float(before.loc[before.value.eq('waiting'),'seconds'].sum()/before.seconds.sum()),
        note='Selected subset with a recorded Resolved state; direct-to-Closed cases excluded; not time to verified restoration')
    text_ids=set(pd.read_sql('SELECT DISTINCT issueid FROM stg_utterances',con).issueid)
    text_scope=status[status.id.isin(text_ids)]
    text_coverage=[]
    for flag in flags:
        frame=text_scope[text_scope.assignment_eligible.eq(1)] if flag=='multiple_handoffs' else text_scope
        text_coverage.append(dict(candidate=flag,text_cases=len(frame),affected_cases=int(frame[flag].sum()),
            unaffected_cases=int((~frame[flag]).sum())))
    pd.DataFrame(text_coverage).to_csv(OUT/'text-candidate-coverage.csv',index=False)
    # Identify concentration with thresholds for tiny groups; no staff ranking.
    projects=status.groupby('issue_proj').agg(cases=('id','size'),waiting_seconds=('waiting_seconds','sum'),
        observed_seconds=('observed_status_seconds','sum'),repeat_waiting=('repeat_waiting','sum'),
        validation_return=('validation_return','sum'),reopened=('reopened','sum'))
    projects['waiting_share']=projects.waiting_seconds/projects.observed_seconds
    projects['repeat_waiting_rate']=projects.repeat_waiting/projects.cases
    projects['share_all_waiting_time']=projects.waiting_seconds/projects.waiting_seconds.sum()
    projects.sort_values('waiting_seconds',ascending=False).to_csv(OUT/'project-concentration.csv')
    top=projects.sort_values('waiting_seconds',ascending=False)
    summary['project_concentration']=dict(projects=len(projects),
        largest_waiting_share=float(top.share_all_waiting_time.iloc[0]),
        top10_waiting_share=float(top.share_all_waiting_time.head(10).sum()))
    # Leave out dominant projects and completed status tails as explicit sensitivity checks.
    checks=[]
    for label,f in [('primary',status),('without_top_waiting_project',status[~status.issue_proj.isin(top.index[:1])]),
        ('without_top10_waiting_projects',status[~status.issue_proj.isin(top.index[:10])]),
        ('created_2019_to_2022',status[status.year.lt(2023)]),
        ('observed_duration_at_most_365_days',status[status.observed_status_seconds.le(365*86400)])]:
        checks.append(dict(scope=label,cases=len(f),waiting_share=float(f.waiting_seconds.sum()/f.observed_status_seconds.sum()),
            repeat_waiting_cases=int(f.repeat_waiting.sum())))
    pd.DataFrame(checks).to_csv(OUT/'waiting-robustness.csv',index=False)
    # Identify exclusions by project/year and recorded resolution without re-admitting them.
    excluded=[]
    for column in ['status_eligible','assignment_eligible']:
        for included,f in primary.groupby(column):
            excluded.append(dict(metric=column,included=int(included),cases=len(f),
                missing_resolution=int(f.recorded_resolution_seconds.isna().sum()),
                median_recorded_resolution_days=float(f.recorded_resolution_seconds.median()/86400)))
    pd.DataFrame(excluded).to_csv(OUT/'exclusion-sensitivity.csv',index=False)
    # Candidate coexistence is not independent impact; never add these populations together.
    binary=status[['repeat_waiting','validation_return','reopened','resolved_holding']].astype(int)
    binary.T.dot(binary).to_csv(OUT/'candidate-overlap.csv')
    primary[['id','year','issue_priority','status_eligible','assignment_eligible','recorded_resolution_seconds']].to_csv(OUT/'baseline-case-register.csv',index=False)
    summary['assignment_only'] = dict(any_named_handoff=int(assignment.any_handoff.sum()),
        multiple_named_handoffs=int(assignment.multiple_handoffs.sum()),
        named_handoff_count=int(assignment.observed_named_handoffs.sum()))
    # Independent source checks of headline aggregations and no-fanout.
    assert len(primary)==con.execute('SELECT SUM(primary_population) FROM cohort_membership').fetchone()[0]
    direct=con.execute('SELECT SUM(duration_seconds) FROM analysis_status_intervals').fetchone()[0]
    assert abs(state_table.observed_seconds.sum()-direct)<.1
    assert set(intervals.issueid)<=set(status.id)
    assert np.isclose(status.waiting_seconds.sum(),state_table.loc['waiting','observed_seconds'])
    summary['verification']='Unique case grain and independent SQL interval totals passed'
    con.close()
    (OUT/'discovery-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2));print(pd.DataFrame(findings).to_string(index=False))

if __name__=='__main__':run()
