"""Milestone 4 episode-level evidence. Does not infer causes or avoidability from flags."""
from pathlib import Path
import hashlib,json,sqlite3
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/milestone4'
DB=ROOT/'data/analytical/service_operations.sqlite'
SEED=20260911

def first_positive_wait(episodes):
    """Keep a real row, including unknown boundaries; never combine group columns."""
    return episodes[episodes.duration_seconds.gt(0)].sort_values(['issueid','created_ts']).drop_duplicates('issueid',keep='first').copy()

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
    e=pd.read_sql((ROOT/'sql/waiting_episodes.sql').read_text(),con)
    assert not e.duplicated(['issueid','created_ts']).any()
    e['episode_id']=e.issueid+'@'+e.created_ts.map(lambda x:format(x,'.6f'))
    e['days']=e.duration_seconds/86400
    e['long_episode']=e.days.ge(7)
    positive=e[e.duration_seconds.gt(0)].copy()
    first=first_positive_wait(e)
    positive.to_csv(OUT/'waiting-episodes.csv',index=False)
    summary={'episode_rows':len(e),'positive_episodes':len(positive),'zero_duration_episodes':int(e.duration_seconds.eq(0).sum()),
             'waiting_cases':int(e.issueid.nunique()),'positive_waiting_cases':int(positive.issueid.nunique()),
             'long_episodes':int(positive.long_episode.sum()),'long_episode_cases':int(positive[positive.long_episode].issueid.nunique()),
             'episode_days_quantiles':positive.days.quantile([.25,.5,.75,.9,.95]).to_dict()}
    summary['repeat_boundary_sensitivity']={str(seconds):int(e[e.duration_seconds.gt(seconds)].groupby('issueid').size().ge(2).sum()) for seconds in [0,60,3600]}
    e.groupby(['previous_state','next_state'],dropna=False).agg(episodes=('issueid','size'),cases=('issueid','nunique'),
        calendar_days=('days','sum'),median_days=('days','median'),long_episodes=('long_episode','sum')).sort_values('calendar_days',ascending=False).to_csv(OUT/'waiting-boundary-paths.csv')
    antecedents=[]
    for col in ['previous_state','prior_validation_returns','prior_named_handoffs','issue_priority','creation_year','issue_proj']:
        frame=first.copy()
        if col in ['prior_validation_returns','prior_named_handoffs']:
            frame['group']=frame[col].map(lambda x:'unknown' if pd.isna(x) else '0' if x==0 else '1' if x==1 else '2+')
        else:frame['group']=frame[col].fillna('unknown').astype(str)
        for group,f in frame.groupby('group'):
            antecedents.append(dict(characteristic=col,group=group,cases=len(f),long_episode_cases=int(f.long_episode.sum()),
                long_episode_rate=float(f.long_episode.mean()),median_wait_days=float(f.days.median())))
    pd.DataFrame(antecedents).to_csv(OUT/'first-wait-antecedents.csv',index=False)
    repeat=e[e.episode_number.gt(1)].copy()
    summary['between_waits']=dict(repeat_episodes=len(repeat),cases=int(repeat.issueid.nunique()),
        with_validation_return=int(repeat.gap_validation_returns.gt(0).sum()),
        cases_with_gap_validation=int(repeat[repeat.gap_validation_returns.gt(0)].issueid.nunique()),
        assignment_known_episodes=int(repeat.gap_named_handoffs.notna().sum()),
        with_named_handoff=int(repeat.gap_named_handoffs.gt(0).sum()),
        cases_with_gap_handoff=int(repeat[repeat.gap_named_handoffs.gt(0)].issueid.nunique()),
        with_both=int((repeat.gap_validation_returns.gt(0)&repeat.gap_named_handoffs.gt(0)).sum()),
        known_with_neither=int((repeat.gap_validation_returns.eq(0)&repeat.gap_named_handoffs.eq(0)).sum()))
    summary['during_wait']=dict(known_assignment_episodes=int(e.during_named_handoffs.notna().sum()),
        episodes_with_named_handoff=int(e.during_named_handoffs.gt(0).sum()))
    # Compare full case characteristics: repeated vs single/no Waiting.
    cases=pd.read_sql((ROOT/'sql/discovery_cases.sql').read_text(),con)
    cases=cases[cases.status_eligible.eq(1)].copy()
    cases['repeat_wait']=cases.waiting_entries.ge(2)
    cases['year']=pd.to_datetime(cases.issue_created,utc=True,format='mixed').dt.year
    characteristics=[]
    for col in ['year','issue_priority','issue_proj']:
        for value,f in cases.groupby(col):
            characteristics.append(dict(characteristic=col,value=str(value),cases=len(f),repeat_cases=int(f.repeat_wait.sum()),
                repeat_rate=float(f.repeat_wait.mean()),share_of_repeat_population=float(f.repeat_wait.sum()/cases.repeat_wait.sum())))
    pd.DataFrame(characteristics).to_csv(OUT/'repeated-case-characteristics.csv',index=False)
    # Do validation returns lead to subsequent Waiting? Immediate next change and next 7 days.
    seq=pd.read_sql("SELECT e.* FROM change_events e JOIN cohort_membership c ON e.issueid=c.id WHERE e.field='status' AND c.status_eligible=1 ORDER BY e.issueid,e.created_ts",con)
    seq['next_state']=seq.groupby('issueid').value.shift(-1)
    bridges=[]
    streams={key:g for key,g in seq.groupby('issueid')}
    for _,r in repeat.iterrows():
        stream=streams[r.issueid]
        between=stream[(stream.created_ts>=r.prior_wait_exit)&(stream.created_ts<r.created_ts)]
        bridges.append(dict(issueid=r.issueid,episode_id=r.episode_id,
            path='waiting > '+' > '.join(between.value.tolist()+['waiting']),
            gap_days=(r.created_ts-r.prior_wait_exit)/86400))
    bridges=pd.DataFrame(bridges)
    bridges.to_csv(OUT/'between-wait-register.csv',index=False)
    bridges.groupby('path').agg(episodes=('issueid','size'),cases=('issueid','nunique'),
        median_gap_days=('gap_days','median')).sort_values('episodes',ascending=False).to_csv(OUT/'between-wait-paths.csv')
    returns=seq[seq.previous_value.eq('validation')&seq.value.eq('in_progress')].copy()
    summary['validation_state_duration_seconds']=(returns.created_ts-returns.previous_ts).quantile([0,.1,.25,.5,.75]).to_dict()
    summary['validation_preceding_state_under_60s']=int((returns.created_ts-returns.previous_ts).lt(60).sum())
    wait_starts={k:g.created_ts.to_numpy() for k,g in e.groupby('issueid')}
    returns['wait_within_7d']=returns.apply(lambda r:bool(((wait_starts.get(r.issueid,np.array([]))>r.created_ts)&(wait_starts.get(r.issueid,np.array([]))<=r.created_ts+7*86400)).any()),axis=1)
    summary['validation_returns']=dict(events=len(returns),cases=int(returns.issueid.nunique()),
        immediate_next_waiting=int(returns.next_state.eq('waiting').sum()),
        waiting_within_7d_events=int(returns.wait_within_7d.sum()),
        waiting_within_7d_cases=int(returns[returns.wait_within_7d].issueid.nunique()))
    returns.groupby('next_state',dropna=False).size().rename('events').to_csv(OUT/'validation-return-next-state.csv')
    returns[['issueid','created_ts','next_state','wait_within_7d']].to_csv(OUT/'validation-return-register.csv',index=False)
    # Downstream outcomes use first positive episode per case, measured AFTER exit.
    outcomes=[]
    for scope,f in [('all_exited',first[first.next_state.notna()]),
        ('endpoint_covers_30d_after_exit',first[first.next_state.notna()&first.ended_ts.ge(first.end_ts+30*86400)])]:
        for long,g in f.groupby('long_episode'):
            outcomes.append(dict(scope=scope,long_episode=bool(long),cases=len(g),
                reopened_30d_cases=int(g.reopen_within_30d.gt(0).sum()),
                reopened_30d_rate=float(g.reopen_within_30d.gt(0).mean()),
                validation_return_30d_cases=int(g.validation_return_within_30d.gt(0).sum()),
                validation_return_30d_rate=float(g.validation_return_within_30d.gt(0).mean())))
    pd.DataFrame(outcomes).to_csv(OUT/'first-wait-downstream-outcomes.csv',index=False)
    sensitivity=[]
    exited=first[first.next_state.notna()]
    for threshold in [3,7,14]:
        for long,g in exited.groupby(exited.days.ge(threshold)):
            sensitivity.append(dict(threshold_days=threshold,long_episode=bool(long),cases=len(g),
                reopen_rate=float(g.reopen_within_30d.gt(0).mean()),
                validation_return_rate=float(g.validation_return_within_30d.gt(0).mean())))
    pd.DataFrame(sensitivity).to_csv(OUT/'downstream-threshold-sensitivity.csv',index=False)
    matched=[]
    for keys,g in first[first.previous_state.isin(['in_progress','validation'])].groupby(['creation_year','issue_priority','issue_proj']):
        a=g[g.previous_state.eq('validation')];b=g[g.previous_state.eq('in_progress')]
        if len(a)>=5 and len(b)>=5:
            matched.append(dict(year=keys[0],priority=keys[1],project=keys[2],validation_cases=len(a),
                in_progress_cases=len(b),validation_long_rate=float(a.long_episode.mean()),
                in_progress_long_rate=float(b.long_episode.mean())))
    pd.DataFrame(matched,columns=['year','priority','project','validation_cases','in_progress_cases','validation_long_rate','in_progress_long_rate']).to_csv(OUT/'preceding-state-overlap-strata.csv',index=False)
    first.groupby(['creation_year','long_episode']).agg(cases=('issueid','size'),
        reopen_30d=('reopen_within_30d',lambda x:x.gt(0).sum()),
        validation_return_30d=('validation_return_within_30d',lambda x:x.gt(0).sum())).to_csv(OUT/'downstream-by-year.csv')
    # Exact next transition (not a fixed-window outcome) has no extra follow-up imputation.
    first.groupby(['long_episode','next_state'],dropna=False).size().rename('cases').to_csv(OUT/'first-wait-next-state.csv')
    # Build purposive review packets. Do not automatically label reason from keywords.
    t=pd.read_sql('SELECT * FROM stg_utterances',con)
    comments=t.sort_values(['issueid','created_ts','comment_seq','utr_seq']).copy()
    comments['utr_num']=pd.to_numeric(comments.utr_seq)
    comments=comments.sort_values(['issueid','created_ts','id','utr_num']).groupby(['issueid','id'],sort=False).agg(
        created_ts=('created_ts','first'),author_role=('author_role','first'),
        text=('actionbody',lambda x:' '.join(x)),source_rows=('source_row',lambda x:','.join(map(str,x)))).reset_index()
    texts=set(t.issueid)
    pool=positive[positive.issueid.isin(texts)].copy()
    pool['stratum']=np.where(pool.long_episode,'long','short')+'_'+np.where(pool.issue_wait_episodes.ge(2),'repeat','single')
    rng=np.random.default_rng(SEED);pool['random_order']=rng.random(len(pool))
    selected=[];used=set()
    for stratum in ['long_repeat','long_single','short_repeat','short_single']:
        candidates=pool[pool.stratum.eq(stratum)].sort_values('random_order')
        projects=set();chosen=[]
        for diversify in [True,False]:
            for _,row in candidates.iterrows():
                if row.issueid in used or (diversify and row.issue_proj in projects):continue
                chosen.append(row);used.add(row.issueid);projects.add(row.issue_proj)
                if len(chosen)==8:break
            if len(chosen)==8:break
        selected.extend(chosen)
    selected=pd.DataFrame(selected)
    selected.to_csv(OUT/'review-sample.csv',index=False)
    packets=[]
    for _,row in selected.iterrows():
        cs=comments[comments.issueid.eq(row.issueid)]
        before=cs[(cs.created_ts<row.created_ts)&(cs.created_ts>=row.created_ts-48*3600)].tail(3)
        during=cs[(cs.created_ts>=row.created_ts)&(cs.created_ts<row.end_ts)]
        if len(during)>4:during=during.iloc[np.unique(np.linspace(0,len(during)-1,4).astype(int))]
        after=cs[(cs.created_ts>=row.end_ts)&(cs.created_ts<=row.end_ts+48*3600)].head(1)
        ctx=[]
        for period,frame in [('before',before),('during',during),('after',after)]:
            for _,r in frame.iterrows():
                ctx.append(dict(period=period,comment_id=r.id,created_utc=str(pd.to_datetime(r.created_ts,unit='s',utc=True)),
                    role=r.author_role,source_rows=r.source_rows,text=r.text[:1600],truncated=len(r.text)>1600))
        packets.append(dict(issueid=row.issueid,episode_id=row.episode_id,stratum=row.stratum,
            project=row.issue_proj,priority=row.issue_priority,days=row.days,
            start_utc=str(pd.to_datetime(row.created_ts,unit='s',utc=True)),
            end_utc=str(pd.to_datetime(row.end_ts,unit='s',utc=True)),
            predecessor=None if pd.isna(row.previous_state) else row.previous_state,
            successor=None if pd.isna(row.next_state) else row.next_state,comments=ctx,
            total_comments_in_episode=int(((cs.created_ts>=row.created_ts)&(cs.created_ts<row.end_ts)).sum())))
    (OUT/'review-packets.json').write_text(json.dumps(packets,indent=2,allow_nan=False),encoding='utf-8')
    # Expanded full-episode context for two substantive case leads; no text truncation.
    expanded=[]
    for issue in ['1007739','1010058']:
        row=selected[selected.issueid.eq(issue)].iloc[0]
        cs=comments[comments.issueid.eq(issue)&comments.created_ts.between(row.created_ts-48*3600,row.end_ts+48*3600)]
        expanded.append(dict(issueid=issue,episode_id=row.episode_id,comments=cs.to_dict('records')))
    (OUT/'expanded-review-packets.json').write_text(json.dumps(expanded,indent=2,allow_nan=False),encoding='utf-8')
    validation_packets=[]
    for _,r in returns[returns.issueid.isin(texts)].iterrows():
        cs=comments[comments.issueid.eq(r.issueid)&comments.created_ts.between(r.created_ts-48*3600,r.created_ts+48*3600)].copy()
        cs['period']=np.where(cs.created_ts.lt(r.created_ts),'before','at_or_after')
        validation_packets.append(dict(issueid=r.issueid,return_ts=r.created_ts,next_state=None if pd.isna(r.next_state) else r.next_state,
            comments=cs.to_dict('records')))
    (OUT/'validation-review-packets.json').write_text(json.dumps(validation_packets,indent=2,allow_nan=False),encoding='utf-8')
    summary['validation_text_coverage']=dict(cases=int(returns[returns.issueid.isin(texts)].issueid.nunique()),events=len(validation_packets))
    summary['review_sample']=selected.stratum.value_counts().to_dict()
    summary['sql_sha256']=hashlib.sha256((ROOT/'sql/waiting_episodes.sql').read_bytes()).hexdigest()
    summary['pipeline_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert np.isclose(e.duration_seconds.sum(),cases.waiting_seconds.sum())
    assert len(returns)==int(cases.validation_returns.sum())
    summary['checks']='episode durations and validation-return totals reconcile to case aggregates'
    (OUT/'mechanism-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    con.close();print(json.dumps(summary,indent=2))

if __name__=='__main__':run()
