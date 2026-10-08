"""Milestone 2: source-preserving staging, SQL process reconstruction and diagnostics."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import hashlib
import json
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/helpdesk_v3'
OUT = ROOT / 'reports/milestone2'
DB = ROOT / 'data/analytical/service_operations.sqlite'


def key(value):
    if value == '' or pd.isna(value):
        return None
    number = Decimal(str(value))
    if not number.is_finite() or number != number.to_integral_value():
        raise ValueError(f'Nonintegral identifier: {value}')
    return str(int(number))


def epoch(series):
    dates = pd.to_datetime(series, format='mixed', errors='coerce', utc=True)
    return (dates-pd.Timestamp('1970-01-01', tz='UTC')).dt.total_seconds()


def read(name, keys, times):
    frame = pd.read_csv(RAW / name, dtype=str, keep_default_na=False)
    frame['source_row'] = range(2, len(frame)+2)
    frame['source_file'] = name
    for col in keys:
        frame[f'{col}_raw'] = frame[col]
        frame[col] = frame[col].map(key)
    for col in times:
        frame[f'{col}_ts'] = epoch(frame[col])
    return frame


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    DB.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/'docs/source-manifest.json').read_text(encoding='utf-8-sig'))
    for item in manifest:
        p = RAW/item['filename']
        if p.suffix != '.png':
            assert hashlib.sha256(p.read_bytes()).hexdigest() == item['content_details']['sha256_hash']
    i = read('issues.csv',['id'],['issue_created','issue_resolution_date','last_change_date','started','ended'])
    h = read('issues_change_history.csv',['id','issueid','change_group_id'],['created'])
    s = read('issues_snapshot.csv',['id'],['started','ended'])
    t = read('sample_utterances.csv',['issueid','id'],['created'])
    i['is_external_project'] = i.issue_proj.str.match(r'^C(?:0[0-9]|1[0-7]).{3,}$').astype(int)
    assert i.id.is_unique and h.id.is_unique
    assert not i.id.isna().any() and not h.id.isna().any()
    # Build into a temporary sibling, preserving the previous complete run on failure.
    temporary = DB.with_suffix('.building.sqlite')
    if temporary.exists():
        temporary.unlink()
    con = sqlite3.connect(temporary)
    try:
        for name,df in [('issues',i),('history',h),('snapshots',s),('utterances',t)]:
            df.to_sql('stg_'+name,con,index=False)
        con.executescript((ROOT/'sql/build_process.sql').read_text())
        q = pd.read_sql('SELECT * FROM issue_quality',con).set_index('id')
        cohorts = pd.read_sql('SELECT * FROM cohort_membership',con).set_index('id')
        cases = i.set_index('id').join(q).join(cohorts)
        cases['year'] = pd.to_datetime(cases.issue_created,format='mixed',utc=True).dt.year
        cases['resolution_days'] = (cases.issue_resolution_date_ts-cases.issue_created_ts)/86400
        measures = pd.read_sql('SELECT * FROM case_observed_measures',con).set_index('id')
        summary = {'source_sha256':{x['filename']:x['content_details']['sha256_hash'] for x in manifest if not x['filename'].endswith('.png')}}
        summary['observation_cutoff_utc'] = str(pd.to_datetime(max(i.last_change_date_ts.max(),h.created_ts.max()),unit='s',utc=True))
        summary['cohorts'] = cohorts.sum().to_dict()
        summary['run_metadata']=dict(pandas_version=pd.__version__,sqlite_version=sqlite3.sqlite_version,
            sql_sha256=hashlib.sha256((ROOT/'sql/build_process.sql').read_bytes()).hexdigest(),
            pipeline_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            primary_start='2019-01-01T00:00:00Z',
            primary_definition='external project pattern and issue_type Ticket',
            interval_boundary='source ended, no assumed time before first observation')
        summary['quality_all'] = {x:int(cases[x].fillna(0).gt(0).sum()) for x in q if x in [
            'events_before_creation','events_after_endpoint','invalid_event_times','status_conflict',
            'assignee_conflict','final_status_mismatch','invalid_bounds','invalid_resolution_bounds']}
        summary['quality_primary'] = {x:int(cases.loc[cases.primary_population.eq(1),x].fillna(0).gt(0).sum()) for x in summary['quality_all']}
        cases.groupby(['issue_type','is_external_project']).size().rename('issues').to_csv(OUT/'type-project-scope.csv')
        annual = cases.groupby(['year','external_ticket']).agg(issues=('issue_type','size'),
            median_recorded_resolution_days=('resolution_days','median'),
            over_365_days=('resolution_days',lambda x:x.gt(365).sum()),
            missing_resolution=('issue_resolution_date',lambda x:x.eq('').sum()),
            no_status=('status_rows',lambda x:x.eq(0).sum()))
        annual.to_csv(OUT/'annual-cohort-diagnostics.csv')
        primary = cases[cases.primary_population.eq(1)]
        sensitivity=[]
        for year in [2016,2017,2018,2019,2020]:
            for scope,flag in [('external_ticket','external_ticket'),('broad_service','broad_service')]:
                subset=cases[cases[flag].eq(1)&cases.year.ge(year)]
                sensitivity.append(dict(start_year=year,scope=scope,issues=len(subset),
                    missing_resolution=int(subset.issue_resolution_date_ts.isna().sum()),
                    median_recorded_resolution_days=float(subset.resolution_days.median()),
                    over_365_days=int(subset.resolution_days.gt(365).sum())))
        pd.DataFrame(sensitivity).to_csv(OUT/'cohort-sensitivity.csv',index=False)
        waterfall = [('All exported issues',len(cases)),('External-project Ticket',int(cases.external_ticket.sum())),
                     ('Created from 2019-01-01',len(primary))]
        eligible = primary.copy()
        for label,mask in [
            ('Has status history',primary.status_rows.gt(0)),
            ('Unambiguous status ordering',primary.status_conflict.eq(0)),
            ('Valid event timestamps',primary.invalid_event_times.eq(0)),
            ('No events before creation',primary.events_before_creation.eq(0)),
            ('No events after source endpoint',primary.events_after_endpoint.eq(0)),
            ('Valid issue bounds',primary.invalid_bounds.eq(0)),
            ('Final status reconciles',primary.final_status_mismatch.eq(0))]:
            eligible = eligible.loc[eligible.index.intersection(primary.index[mask])]
            waterfall.append((label,len(eligible)))
        pd.DataFrame(waterfall,columns=['step','remaining_issues']).to_csv(OUT/'cohort-waterfall.csv',index=False)
        # Raw chronology diagnostics; source order is not the process order.
        summary['history'] = dict(
            source_order_backsteps=int(h.groupby(['issueid','field']).created_ts.diff().lt(0).sum()),
            exact_semantic_duplicates=int(h.duplicated(['issueid','field','created_ts','value']).sum()),
            unknown_fields=sorted(set(h.field)-{'status','assignee'}),
            orphan_rows=int((~h.issueid.isin(i.id)).sum()))
        conflict = pd.read_sql('SELECT * FROM event_conflicts',con)
        conflict.to_csv(OUT/'event-conflicts.csv',index=False)
        summary['conflict_groups'] = len(conflict)
        groups = h.groupby('change_group_id').agg(issues=('issueid','nunique'),times=('created_ts','nunique'))
        summary['change_groups'] = dict(multiple_issues=int(groups.issues.gt(1).sum()),multiple_timestamps=int(groups.times.gt(1).sum()))
        # Compare observed durations only, retaining the unknown prefix before first event.
        intervals = pd.read_sql("SELECT * FROM observed_intervals WHERE field='status'",con)
        observed = intervals.pivot_table(index='issueid',columns='value',values='duration_seconds',aggfunc='sum')
        reconciliation=[]
        for state in observed.columns:
            col='wf_'+state
            if col not in cases:
                continue
            actual=observed[state].dropna()
            published=pd.to_numeric(cases.loc[actual.index,col],errors='coerce')
            # Only for this reconciliation: zero visits + blank residence time is structural zero.
            visits=pd.to_numeric(cases.loc[actual.index,'wfe_'+state],errors='coerce')
            comparison_value=published.mask(published.isna()&visits.eq(0),0)
            diff=(actual-comparison_value).abs()
            good=cases.loc[actual.index,'status_eligible'].eq(1)
            reconciliation.append(dict(state=state,observed_issues=len(actual),
                publisher_nonblank=int(published.notna().sum()),within_1_second=int(diff.le(1).sum()),
                primary_eligible_observed=int(good.sum()),
                primary_eligible_within_1_second=int((diff.le(1)&good).sum())))
        pd.DataFrame(reconciliation).to_csv(OUT/'state-duration-reconciliation.csv',index=False)
        wf=[x for x in i if x.startswith('wf_') and x!='wf_total_time']
        wfe=[x for x in i if x.startswith('wfe_')]
        totals=i[wf].apply(pd.to_numeric,errors='coerce').sum(axis=1,min_count=1)
        published_total=pd.to_numeric(i.wf_total_time,errors='coerce')
        counts=i[wfe].apply(pd.to_numeric,errors='coerce').sum(axis=1,min_count=1)
        summary['publisher_reconciliation']=dict(
            sum_state_times_matches_total=int((totals-published_total).abs().le(1).sum()),
            sum_visits_matches_steps=int((counts-pd.to_numeric(i.processing_steps)).eq(0).sum()),
            total_matches_endpoint_elapsed=int((published_total-(i.ended_ts-i.issue_created_ts)).abs().le(1).sum()),
            total_matches_recorded_resolution=int((published_total-(i.issue_resolution_date_ts-i.issue_created_ts)).abs().le(1).sum()))
        summary['publisher_reconciliation']['all_state_times_blank']=int(i[wf].eq('').all(axis=1).sum())
        negative=i[wf].apply(pd.to_numeric,errors='coerce').lt(0).any(axis=1)
        summary['publisher_reconciliation']['issues_with_negative_state_time']=int(negative.sum())
        summary['publisher_reconciliation']['primary_with_negative_state_time']=int(i.id[negative].isin(primary.index).sum())
        pub_audit=pd.DataFrame({'id':i.id,'negative_state_time':negative,
            'state_sum_minus_total':totals-published_total,
            'total_minus_endpoint_seconds':published_total-(i.ended_ts-i.issue_created_ts),
            'total_minus_recorded_resolution_seconds':published_total-(i.issue_resolution_date_ts-i.issue_created_ts)})
        pub_audit.to_csv(OUT/'publisher-measure-audit.csv',index=False)
        null_pairs=[]
        for col in wf:
            visit=pd.to_numeric(i['wfe_'+col[3:]],errors='coerce')
            val=pd.to_numeric(i[col],errors='coerce')
            null_pairs.append(dict(state=col[3:],blank_time_zero_visits=int((val.isna()&visit.eq(0)).sum()),
                blank_time_positive_visits=int((val.isna()&visit.gt(0)).sum()),
                numeric_time_zero_visits=int((val.notna()&visit.eq(0)).sum()),negative_time=int(val.lt(0).sum())))
        pd.DataFrame(null_pairs).to_csv(OUT/'state-null-semantics.csv',index=False)
        # Snapshot boundary reconciliation: no backfilling of initial owner.
        s['turn_number']=pd.to_numeric(s.turn,errors='coerce')
        ss=s.sort_values(['id','started_ts','turn_number'])
        previous_end=ss.groupby('id').ended_ts.shift()
        summary['snapshots']=dict(duplicate_issue_turn=int(s.duplicated(['id','turn']).sum()),
            overlaps=int(ss.started_ts.lt(previous_end).sum()),gaps=int(ss.started_ts.gt(previous_end).sum()),
            negative_intervals=int(s.ended_ts.lt(s.started_ts).sum()),
            zero_intervals=int(s.ended_ts.eq(s.started_ts).sum()))
        snap_agg=s.groupby('id').agg(start=('started_ts','min'),end=('ended_ts','max'),cycles=('id','size'))
        summary['snapshots']['start_matches_creation']=int(snap_agg.start.eq(cases.issue_created_ts).sum())
        summary['snapshots']['end_matches_endpoint']=int(snap_agg.end.eq(cases.ended_ts).sum())
        assignee_intervals=pd.read_sql("SELECT * FROM observed_intervals WHERE field='assignee'",con)
        matches=s.merge(assignee_intervals[['issueid','created_ts','end_ts','value']],
            left_on=['id','started_ts','ended_ts','issue_assignee'],right_on=['issueid','created_ts','end_ts','value'],how='left',indicator=True)
        summary['snapshots']['exact_observed_cycle_matches']=int(matches['_merge'].eq('both').sum())
        summary['snapshots']['later_cycles']=int(matches.turn_number.gt(1).sum())
        summary['snapshots']['later_cycles_exact_matches']=int((matches.turn_number.gt(1)&matches['_merge'].eq('both')).sum())
        first_assignee=pd.read_sql("SELECT issueid,value,created_ts FROM change_events WHERE field='assignee' AND previous_ts IS NULL",con).set_index('issueid')
        first_snapshot=ss.groupby('id').first()
        joined=first_snapshot.join(first_assignee,how='inner')
        summary['snapshots']['first_owner_backfilled_before_first_observation']=int((joined.issue_assignee.eq(joined.value)&joined.started_ts.lt(joined.created_ts)).sum())
        # Text metadata and sample coverage, not independent utterance examples.
        appraisal=pd.read_excel(RAW/'issues_snapshot_sample.xlsx',dtype=str).fillna('')
        appraisal['issue_id']=appraisal.id.map(key)
        text_cases=set(t.issueid); app_cases=set(appraisal.issue_id)
        tc=cases.loc[sorted(text_cases)]
        summary['text']=dict(issues=len(text_cases),appraisal_issues=len(app_cases),
            appraisal_rows=len(appraisal),text_without_appraisal=len(text_cases-app_cases),
            appraisal_without_text=len(app_cases-text_cases),
            primary_population=int(tc.primary_population.sum()),status_eligible=int(tc.status_eligible.sum()),
            assignment_eligible=int(tc.assignment_eligible.sum()),
            duplicate_utterance_key=int(t.duplicated(['issueid','id','utr_seq']).sum()),
            issue_types=tc.issue_type.value_counts().to_dict(),
            creation_years=tc.year.value_counts().sort_index().to_dict())
        tj=t.merge(i[['id','issue_created_ts','issue_resolution_date_ts','ended_ts']],left_on='issueid',right_on='id',suffixes=('','_issue'))
        summary['text']['utterances_before_creation']=int(tj.created_ts.lt(tj.issue_created_ts).sum())
        summary['text']['utterances_after_recorded_resolution']=int(tj.created_ts.gt(tj.issue_resolution_date_ts).sum())
        summary['text']['utterances_after_endpoint']=int(tj.created_ts.gt(tj.ended_ts).sum())
        comments=t.groupby(['issueid','id']).agg(times=('created_ts','nunique'),roles=('author_role','nunique'),authors=('author','nunique'),
            sequences=('comment_seq','nunique'))
        summary['text']['inconsistent_comment_metadata']=int(comments.gt(1).any(axis=1).sum())
        sample_ids=i[i.id.isin(text_cases)&i.issue_type.eq('Ticket')].sample(8,random_state=20260911).id.tolist()
        summary['text']['qualitative_review_issue_ids']=sample_ids
        comparison=[]
        for scope,frame in [('primary_population',primary),('primary_2022',primary[primary.year.eq(2022)]),('text_primary',tc[tc.primary_population.eq(1)])]:
            for priority,n in frame.issue_priority.value_counts().items():
                comparison.append(dict(scope=scope,priority=priority,issues=int(n),share=float(n/len(frame))))
        pd.DataFrame(comparison).to_csv(OUT/'text-sample-priority-comparison.csv',index=False)
        endpoint=i[['id','issue_created_ts','ended_ts']].set_index('id')
        firsts=pd.read_sql('SELECT issueid,field,MIN(created_ts) first_ts FROM observed_events GROUP BY issueid,field',con)
        initial=firsts.join(endpoint,on='issueid')
        initial['unobserved_prefix_seconds']=initial.first_ts-initial.issue_created_ts
        initial.to_csv(OUT/'unobserved-prefixes.csv',index=False)
        primary_prefix=initial[initial.issueid.isin(primary.index)&initial.field.eq('status')]
        summary['initial_status_coverage_primary']=dict(issues=len(primary_prefix),
            first_update_after_creation=int(primary_prefix.unobserved_prefix_seconds.gt(0).sum()),
            median_unobserved_prefix_seconds=float(primary_prefix.unobserved_prefix_seconds.median()))
        # Metadata-only dictionary: no text content is copied into report outputs.
        dictionary=[]
        for table,frame in [('issues',i),('history',h),('snapshots',s),('utterances',t)]:
            for col in frame:
                if col.endswith('_ts'):
                    meaning='UTC epoch seconds parsed from '+col[:-3]; use='event-time filter; no rounding'
                elif col in ['source_row','source_file'] or col.endswith('_raw'):
                    meaning='Source lineage'; use='audit only'
                elif col.startswith('wfe_'):
                    meaning='Publisher interval/visit count for '+col[4:]; use='retrospective only; not intake feature'
                elif col.startswith('wf_'):
                    meaning='Publisher seconds in state or total'; use='retrospective; use independently reconstructed measures instead'
                elif col=='actionbody':
                    meaning='Masked sampled utterance'; use='only after its comment timestamp; untrusted content'
                elif col in ['field','value','created','issueid','id','change_group_id','comment_seq','utr_seq','author','author_role','is_private']:
                    meaning='Source identifier or event/comment attribute; see source FEATURES.md'; use='event-time data; identifiers not predictive features'
                else:
                    meaning='Source attribute or derived staging field; see source FEATURES.md'; use='retrospective until intake availability proven'
                dictionary.append(dict(table=table,column=col,meaning=meaning,prediction_use=use))
        pd.DataFrame(dictionary).to_csv(OUT/'data-dictionary.csv',index=False)
        closure=cases.assign(resolution_day=cases.issue_resolution_date.str[:10]).groupby('resolution_day').agg(
            issues=('issue_type','size'),external_tickets=('external_ticket','sum'),median_age_days=('resolution_days','median'),
            over_365_days=('resolution_days',lambda x:x.gt(365).sum()))
        closure.sort_values('issues',ascending=False).head(25).to_csv(OUT/'resolution-date-concentrations.csv')
        pd.read_sql("SELECT previous_value,value,COUNT(*) transitions,COUNT(DISTINCT issueid) issues FROM status_transitions GROUP BY previous_value,value ORDER BY transitions DESC",con).to_csv(OUT/'validated-status-transitions.csv',index=False)
        cases.reset_index()[['id','source_row','source_file','issue_type','issue_proj','year']+list(cohorts.columns)+list(q.columns)].to_csv(OUT/'case-quality-register.csv',index=False)
        summary['endpoint_comparison_primary']=dict(
            eligible_status_issues=int(primary.status_eligible.sum()),
            has_recorded_resolution=int(primary.issue_resolution_date_ts.notna().sum()),
            first_resolved_and_recorded_differ_over_60_seconds=int(((measures.loc[primary.index,'first_resolved_state_seconds']-measures.loc[primary.index,'recorded_resolution_seconds']).abs()>60).sum()))
        con.execute('CREATE INDEX interval_issue ON observed_intervals(issueid,field)')
        con.commit()
        summary['integrity_check']=con.execute('PRAGMA integrity_check').fetchone()[0]
        summary['analytical_counts']={name:con.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]
            for name in ['observed_events','change_events','observed_intervals','issue_quality','cohort_membership','case_observed_measures']}
        (OUT/'validation-summary.json').write_text(json.dumps(summary,indent=2,default=lambda x:int(x)),encoding='utf-8')
        print(json.dumps(summary,indent=2,default=lambda x:int(x)))
    finally:
        con.close()
    temporary.replace(DB)


if __name__=='__main__':
    run()
