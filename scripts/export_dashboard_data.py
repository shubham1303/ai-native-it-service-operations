"""Flat CSVs for the Power BI dashboard. Same population and definitions as Milestone 3."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/dashboard'
DB=ROOT/'data/analytical/service_operations.sqlite'
DAY=86400

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
    # reuse the discovery query so every number lines up with the milestone reports
    cases=pd.read_sql((ROOT/'sql/discovery_cases.sql').read_text(),con)
    t=cases[cases.primary_population.eq(1)].copy()
    created=pd.to_datetime(t.issue_created_ts,unit='s',utc=True)
    status_ok=t.status_eligible.eq(1)
    tickets=pd.DataFrame({
        'ticket_id':t.id,
        'created_date':created.dt.strftime('%Y-%m-%d'),
        'project':t.issue_proj,
        'priority':t.issue_priority.fillna('unknown'),
        'final_status':t.issue_status,
        'status_eligible':status_ok.astype(int),
        'assignment_eligible':t.assignment_eligible.astype(int),
        'resolution_days':t.recorded_resolution_seconds/DAY,
        # status measures only exist for status-eligible tickets; leave the rest blank, not zero
        'observed_status_days':(t.observed_status_seconds.fillna(0)/DAY).where(status_ok),
        'waiting_days':(t.waiting_seconds.fillna(0)/DAY).where(status_ok),
        'waiting_entries':t.waiting_entries.fillna(0).where(status_ok),
        'validation_returns':t.validation_returns.fillna(0).where(status_ok),
        'reopen_entries':t.reopen_entries.fillna(0).where(status_ok),
        'named_handoffs':t.observed_named_handoffs.where(t.assignment_eligible.eq(1)),
    })
    for col in ['waiting_entries','validation_returns','reopen_entries','named_handoffs']:
        tickets[col]=tickets[col].astype('Int64')  # write 2, not 2.0; blanks stay blank
    tickets.to_csv(OUT/'tickets.csv',index=False)

    intervals=pd.read_sql('SELECT issueid,value,created_ts,duration_seconds FROM analysis_status_intervals',con)
    intervals=intervals[intervals.issueid.isin(tickets.ticket_id[status_ok])]
    status_time=(intervals.groupby(['issueid','value'],as_index=False)
        .agg(seconds=('duration_seconds','sum'),intervals=('value','size')))
    status_time['days']=status_time.seconds/DAY
    status_time.rename(columns={'issueid':'ticket_id','value':'status'})[['ticket_id','status','days','intervals']]\
        .to_csv(OUT/'status_time.csv',index=False)

    waits=intervals[intervals.value.eq('waiting')].sort_values(['issueid','created_ts']).copy()
    waits['episode_number']=waits.groupby('issueid').cumcount()+1
    waits['days']=waits.duration_seconds/DAY
    waits['started_date']=pd.to_datetime(waits.created_ts,unit='s',utc=True).dt.strftime('%Y-%m-%d')
    waits.rename(columns={'issueid':'ticket_id'})[['ticket_id','episode_number','started_date','days']]\
        .to_csv(OUT/'waiting_episodes.csv',index=False)

    # quick check against the published milestone numbers
    share=status_time.loc[status_time.value.eq('waiting'),'seconds'].sum()/status_time.seconds.sum()
    print(f'tickets {len(tickets)}, status-eligible {int(status_ok.sum())}, '
          f'median resolution {tickets.resolution_days.median():.2f}d, waiting share {share:.4f}, '
          f'repeat waiting {int((tickets.waiting_entries>=2).sum())}, positive episodes {int((waits.days>0).sum())}')

if __name__=='__main__':
    run()
