"""Read-only initial source profiling. No business problem or model is assumed."""
from pathlib import Path
import csv
import gzip
import hashlib
import json
import sqlite3
import xml.etree.ElementTree as ET
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/helpdesk_v3'
OUT = ROOT / 'reports'


def profile():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads((RAW / 'source-manifest.json').read_text(encoding='utf-8-sig'))
    checksums = {}
    for item in manifest:
        path = RAW / item['filename']
        if path.exists():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual == item['content_details']['sha256_hash'], path.name
            checksums[path.name] = actual
    tables, profiles, columns = {}, {}, []
    for path in sorted(RAW.glob('*.csv')):
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8-sig')
        # Independently validate parser row counts, including multiline messages.
        with path.open(encoding='utf-8-sig', newline='') as source:
            assert sum(1 for _ in csv.reader(source)) - 1 == len(df)
        tables[path.stem] = df
        profiles[path.name] = dict(rows=len(df), columns=len(df.columns),
                                   exact_duplicate_rows=int(df.duplicated().sum()))
        for col in df:
            s = df[col]
            nonempty = s[s.str.strip().ne('')]
            columns.append(dict(file=path.name, column=col, rows=len(s),
                                blank=int(s.str.strip().eq('').sum()),
                                distinct_nonblank=int(nonempty.nunique()),
                                whitespace_values=int(s.ne(s.str.strip()).sum()),
                                replacement_characters=int(s.str.contains('\ufffd', regex=False).sum())))
    issues = tables['issues']
    history = tables['issues_change_history']
    text = tables['sample_utterances']
    snapshots = tables['issues_snapshot']
    stats = dict(files=profiles, checksums=checksums, timestamps={}, categories={})
    for name, df in tables.items():
        for col in ['started', 'ended', 'created', 'issue_created', 'issue_resolution_date', 'last_change_date']:
            if col not in df:
                continue
            parsed = pd.to_datetime(df[col], errors='coerce', utc=True, format='mixed')
            stats['timestamps'][f'{name}.{col}'] = dict(
                blank=int(df[col].eq('').sum()),
                invalid_nonblank=int((parsed.isna() & df[col].ne('')).sum()),
                minimum=str(parsed.min()), maximum=str(parsed.max()))
    for col in ['issue_type', 'issue_priority', 'issue_status', 'issue_resolution']:
        stats['categories'][col] = issues[col].value_counts(dropna=False).to_dict()
    stats['categories']['history_fields'] = history['field'].value_counts().to_dict()
    stats['categories']['history_status_values'] = history.loc[history.field.eq('status'), 'value'].value_counts().to_dict()
    stats['categories']['author_roles'] = text['author_role'].value_counts().to_dict()
    # Source IDs are numeric-looking strings. Preserve them exactly for joins.
    with sqlite3.connect(':memory:') as con:
        for name in ['issues', 'issues_change_history', 'issues_snapshot', 'sample_utterances']:
            tables[name].to_sql(name, con, index=False)
        con.execute('CREATE INDEX issue_key ON issues(id)')
        con.execute('CREATE INDEX history_issue_key ON issues_change_history(issueid)')
        queries = json.loads((ROOT / 'sql/profile_queries.json').read_text())
        stats['relational_checks'] = {name: pd.read_sql_query(query, con).to_dict('records')
                                      for name, query in queries.items()}
    for name, df, key in [('issues', issues, 'id'), ('history', history, 'id')]:
        stats[f'{name}_duplicate_keys'] = int(df.duplicated(key).sum())
    c = pd.to_datetime(issues.issue_created, utc=True, errors='coerce', format='mixed')
    r = pd.to_datetime(issues.issue_resolution_date, utc=True, errors='coerce', format='mixed')
    delta = (r-c).dt.total_seconds()
    stats['duration_quality'] = dict(negative_resolution_durations=int(delta.lt(0).sum()),
                                   zero_resolution_durations=int(delta.eq(0).sum()),
                                   missing_resolution=int(r.isna().sum()),
                                   resolution_over_365_days=int(delta.gt(365*86400).sum()))
    stats['issue_created_by_year'] = c.dt.year.value_counts().sort_index().to_dict()
    status = history.loc[history.field.eq('status')].copy()
    status['timestamp'] = pd.to_datetime(status.created, utc=True, errors='coerce', format='mixed')
    tied = status.duplicated(['issueid', 'timestamp'], keep=False)
    stats['status_rows_at_tied_timestamps'] = int(tied.sum())
    stats['status_cases_with_ties'] = int(status.loc[tied, 'issueid'].nunique())
    # Entire tied/invalid cases excluded from preliminary sequencing, never invent order.
    excluded = set(status.loc[tied | status.timestamp.isna(), 'issueid'])
    ordered = status.loc[~status.issueid.isin(excluded)].sort_values(['issueid', 'timestamp'])
    ordered['previous'] = ordered.groupby('issueid')['value'].shift()
    transitions = ordered.dropna(subset=['previous']).groupby(['previous', 'value']).size()
    transitions.sort_values(ascending=False).rename('count').to_csv(OUT / 'initial-status-transitions.csv')
    stats['transition_scope'] = dict(cases=int(ordered.issueid.nunique()),
                                   excluded_cases=len(excluded), rows=len(ordered))
    stats['text'] = dict(unique_issues=int(text['issueid' if 'issueid' in text else 'issuedid'].nunique()),
                        distinct_comments=int(text['id'].nunique()),
                        blank_utterances=int(text.actionbody.str.strip().eq('').sum()),
                        placeholder_utterances=int(text.actionbody.str.contains(r'\bph_\w+').sum()))
    numeric_cols = [x for x in issues if x.startswith(('wf_', 'wfe_'))] + ['processing_steps']
    stats['numeric_quality'] = {}
    for col in numeric_cols:
        n = pd.to_numeric(issues[col], errors='coerce')
        stats['numeric_quality'][col] = dict(negative=int(n.lt(0).sum()),
            invalid_nonblank=int((n.isna() & issues[col].ne('')).sum()))
    sample = pd.read_excel(RAW / 'issues_snapshot_sample.xlsx', sheet_name=None)
    stats['appraisal_workbook'] = {name: dict(rows=len(df), columns=list(df.columns)) for name, df in sample.items()}
    pd.DataFrame(columns).to_csv(OUT / 'column-profile.csv', index=False)
    (OUT / 'initial-profile.json').write_text(json.dumps(stats, indent=2), encoding='utf-8')
    comparisons = {}
    for path in (ROOT / 'data/research').glob('*.csv'):
        df = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False, encoding='utf-8-sig')
        comparisons[path.name] = dict(rows=len(df), columns=list(df.columns),
            blank_incident_rows=int(df['Incident ID'].str.strip().eq('').sum()) if 'Incident ID' in df else None,
            unique_incidents=int(df.loc[df['Incident ID'].str.strip().ne(''), 'Incident ID'].nunique()) if 'Incident ID' in df else None)
    path = ROOT / 'data/research/BPI_Challenge_2013_incidents.xes.gz'
    with gzip.open(path) as f:
        tree = ET.parse(f)
    traces = tree.findall('{*}trace')
    events = [e for t in traces for e in t.findall('{*}event')]
    comparisons[path.name] = dict(cases=len(traces), events=len(events),
        trace_fields=sorted({c.attrib.get('key','') for t in traces for c in t if not c.tag.endswith('event')}),
        event_fields=sorted({c.attrib.get('key','') for e in events for c in e}))
    (OUT / 'comparison-file-inspection.json').write_text(json.dumps(comparisons, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in stats.items() if k not in ['checksums','numeric_quality','categories','timestamps']}, indent=2))
    print(json.dumps(comparisons, indent=2))


if __name__ == '__main__':
    profile()
