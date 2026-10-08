"""Milestone 4 safeguards for temporality, grain and qualitative evidence lineage."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/analytical/service_operations.sqlite'
OUT=ROOT/'reports/milestone4'
spec=importlib.util.spec_from_file_location('mechanisms',ROOT/'scripts/validate_mechanisms.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class FirstEpisodeContract(unittest.TestCase):
    def test_unknown_boundary_is_not_backfilled_from_a_later_episode(self):
        fixture=pd.DataFrame([
            dict(issueid='case',created_ts=0,duration_seconds=0,previous_state='open'),
            dict(issueid='case',created_ts=1,duration_seconds=20,previous_state=None),
            dict(issueid='case',created_ts=30,duration_seconds=40,previous_state='validation')])
        row=module.first_positive_wait(fixture).iloc[0]
        self.assertEqual(row.created_ts,1)
        self.assertTrue(pd.isna(row.previous_state))

@unittest.skipUnless(DB.exists() and (OUT/'review-metadata.json').exists(),'Build Milestone 4 evidence first')
class MechanismContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
        cls.e=pd.read_sql((ROOT/'sql/waiting_episodes.sql').read_text(),cls.con)
        cls.events=pd.read_sql("SELECT * FROM change_events WHERE field='status' ORDER BY issueid,created_ts",cls.con)
    @classmethod
    def tearDownClass(cls):cls.con.close()
    def test_episode_grain_and_elapsed_time_reconcile(self):
        self.assertFalse(self.e.duplicated(['issueid','created_ts']).any())
        expected=self.con.execute("SELECT COUNT(*),SUM(duration_seconds) FROM analysis_status_intervals WHERE value='waiting'").fetchone()
        self.assertEqual(len(self.e),expected[0])
        self.assertAlmostEqual(self.e.duration_seconds.sum(),expected[1],places=3)
        self.assertTrue(self.e.duration_seconds.ge(0).all())
    def test_real_adjacent_states_include_unknown_prefix(self):
        lookup={key:list(zip(g.created_ts,g.value)) for key,g in self.events.groupby('issueid')}
        for r in self.e.itertuples():
            stream=lookup[r.issueid];idx=next(i for i,(t,v) in enumerate(stream) if t==r.created_ts)
            self.assertEqual(stream[idx][1],'waiting')
            prev=stream[idx-1][1] if idx else None
            nxt=stream[idx+1][1] if idx+1<len(stream) else None
            self.assertEqual(None if pd.isna(r.previous_state) else r.previous_state,prev)
            self.assertEqual(None if pd.isna(r.next_state) else r.next_state,nxt)
    def test_prior_and_downstream_counts_use_correct_time_sides(self):
        for r in self.e.sample(100,random_state=20260911).itertuples():
            g=self.events[self.events.issueid.eq(r.issueid)]
            returns=g[g.previous_value.eq('validation')&g.value.eq('in_progress')]
            self.assertEqual(r.prior_validation_returns,int(returns.created_ts.lt(r.created_ts).sum()))
            downstream=returns.created_ts.gt(r.end_ts)&returns.created_ts.le(r.end_ts+30*86400)
            self.assertEqual(r.validation_return_within_30d,int(downstream.sum()))
        self.assertTrue(self.e.loc[self.e.assignment_eligible.eq(0),'prior_named_handoffs'].isna().all())
    def test_downstream_denominator_is_one_exited_positive_episode_per_case(self):
        first=module.first_positive_wait(self.e)
        report=pd.read_csv(OUT/'first-wait-downstream-outcomes.csv')
        self.assertTrue(first.issueid.is_unique)
        self.assertEqual(int(report[report.scope.eq('all_exited')].cases.sum()),int(first.next_state.notna().sum()))
    def test_review_evidence_matches_original_case_comment_and_rows(self):
        lookup={}
        for issue,comment,row in self.con.execute('SELECT issueid,id,source_row FROM stg_utterances'):
            lookup.setdefault((issue,comment),set()).add(str(row))
        for filename in ['waiting-review-register.json','validation-review-register.json']:
            for r in json.loads((OUT/filename).read_text()):
                for ev in r['evidence']:
                    comment=ev.get('comment_id',ev.get('id'))
                    self.assertEqual(set(ev['source_rows'].split(',')),lookup[(r['issueid'],comment)])
        sample=pd.read_csv(OUT/'review-sample.csv',dtype={'issueid':str})
        self.assertTrue(sample.issueid.is_unique)
        self.assertEqual(sample.groupby('stratum').size().tolist(),[8,8,8,8])
    def test_judgments_are_bound_to_reviewed_packets(self):
        meta=json.loads((OUT/'review-metadata.json').read_text())
        for name,digest in meta['packet_sha256'].items():
            self.assertEqual(hashlib.sha256((OUT/name).read_bytes()).hexdigest(),digest)

if __name__=='__main__':unittest.main()
