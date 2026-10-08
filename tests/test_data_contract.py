"""Contracts against the generated database, independent of diagnostic summaries."""
from pathlib import Path
import sqlite3
import unittest

DB=Path(__file__).resolve().parents[1]/'data/analytical/service_operations.sqlite'

@unittest.skipUnless(DB.exists(),'Run validate_process.py first')
class DataContracts(unittest.TestCase):
    def setUp(self):
        self.con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
        self.addCleanup(self.con.close)
    def scalar(self,sql):
        return self.con.execute(sql).fetchone()[0]
    def test_issue_population_preserved(self):
        n=self.scalar('SELECT COUNT(*) FROM stg_issues')
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM cohort_membership'),n)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM issue_quality'),n)
    def test_event_lineage_reconciles(self):
        included=self.scalar('SELECT SUM(source_event_count) FROM observed_events')
        excluded=self.scalar('''SELECT COUNT(*) FROM stg_history h WHERE EXISTS
        (SELECT 1 FROM event_conflicts c WHERE c.issueid=h.issueid AND c.field=h.field)''')
        self.assertEqual(included+excluded,self.scalar('SELECT COUNT(*) FROM stg_history'))
    def test_intervals_never_negative_or_outside_bounds(self):
        self.assertEqual(self.scalar('''SELECT COUNT(*) FROM observed_intervals
        WHERE duration_seconds<0 OR created_ts<issue_created_ts OR end_ts>ended_ts'''),0)
    def test_consumer_views_exclude_ineligible_cases(self):
        self.assertEqual(self.scalar('''SELECT COUNT(*) FROM analysis_status_intervals e
        JOIN cohort_membership c ON c.id=e.issueid WHERE c.status_eligible<>1'''),0)
        self.assertEqual(self.scalar('''SELECT COUNT(*) FROM analysis_case_measures
        WHERE status_eligible=0 AND observed_waiting_seconds IS NOT NULL'''),0)
    def test_primary_definition_not_outcome_conditioned(self):
        self.assertGreater(self.scalar('''SELECT COUNT(*) FROM stg_issues i
        JOIN cohort_membership c ON c.id=i.id WHERE c.primary_population=1 AND i.issue_resolution_date='' '''),0)
    def test_event_keys_and_orphans(self):
        self.assertEqual(self.scalar('''SELECT COUNT(*) FROM stg_history h LEFT JOIN stg_issues i
        ON i.id=h.issueid WHERE i.id IS NULL'''),0)
        self.assertEqual(self.scalar('SELECT COUNT(*)-COUNT(DISTINCT id) FROM stg_history'),0)

if __name__=='__main__':unittest.main()
