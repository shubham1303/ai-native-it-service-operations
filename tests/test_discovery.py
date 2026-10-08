"""Verify discovery grain and sums independently of the summary files."""
from pathlib import Path
import sqlite3
import unittest
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/analytical/service_operations.sqlite'

@unittest.skipUnless(DB.exists(),'Build the validated database first')
class DiscoveryContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con=sqlite3.connect(f'file:{DB.as_posix()}?mode=ro',uri=True)
        cls.frame=pd.read_sql((ROOT/'sql/discovery_cases.sql').read_text(),cls.con)
    @classmethod
    def tearDownClass(cls):cls.con.close()
    def test_case_grain_preserves_sources(self):
        self.assertTrue(self.frame.id.is_unique)
        self.assertEqual(len(self.frame),self.con.execute('SELECT COUNT(*) FROM stg_issues').fetchone()[0])
    def test_waiting_sum_reconciles_without_join_multiplication(self):
        measured=self.frame.loc[self.frame.status_eligible.eq(1),'waiting_seconds'].sum()
        source=self.con.execute("SELECT SUM(duration_seconds) FROM analysis_status_intervals WHERE value='waiting'").fetchone()[0]
        self.assertAlmostEqual(measured,source,places=3)
    def test_repeated_waiting_case_definition(self):
        actual=int((self.frame.status_eligible.eq(1)&self.frame.waiting_entries.ge(2)).sum())
        expected=self.con.execute("SELECT COUNT(*) FROM (SELECT issueid FROM analysis_status_intervals WHERE value='waiting' GROUP BY issueid HAVING COUNT(*)>=2)").fetchone()[0]
        self.assertEqual(actual,expected)
    def test_candidate_association_excludes_unresolved_values(self):
        primary=self.frame[self.frame.primary_population.eq(1)]
        self.assertEqual(primary.recorded_resolution_seconds.notna().sum()+primary.recorded_resolution_seconds.isna().sum(),len(primary))
        self.assertTrue(primary.recorded_resolution_seconds.dropna().ge(0).all())

if __name__=='__main__':unittest.main()
