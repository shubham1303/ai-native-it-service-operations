"""Synthetic fixtures for SQL safety and timeline semantics; never historical evidence."""
from pathlib import Path
import sqlite3
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_process import key

SQL=(Path(__file__).resolve().parents[1]/'sql/build_process.sql').read_text()
START=1546300800

class ProcessTests(unittest.TestCase):
    def build(self,events,final='closed',end=100):
        con=sqlite3.connect(':memory:')
        con.executescript('''
        CREATE TABLE stg_issues(id TEXT,issue_created_ts REAL,ended_ts REAL,issue_resolution_date_ts REAL,
          issue_status TEXT,is_external_project INTEGER,issue_type TEXT);
        CREATE TABLE stg_history(id TEXT,issueid TEXT,field TEXT,value TEXT,created_ts REAL,source_row INTEGER);
        CREATE TABLE stg_snapshots(id TEXT);
        ''')
        con.execute('INSERT INTO stg_issues VALUES (?,?,?,?,?,?,?)',('1',START,START+end,START+80,final,1,'Ticket'))
        for n,(field,value,second) in enumerate(events):
            con.execute('INSERT INTO stg_history VALUES (?,?,?,?,?,?)',
                (str(n),'1',field,value,None if second is None else START+second,n+2))
        con.executescript(SQL)
        self.addCleanup(con.close)
        return con

    def test_order_duplicates_and_unknown_initial_state(self):
        c=self.build([('status','closed',100),('status','in_progress',10),
                      ('status','in_progress',10),('status','in_progress',15),('status','resolved',40)])
        self.assertEqual(c.execute("SELECT duration_seconds FROM observed_intervals WHERE value='in_progress'").fetchone()[0],30)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM change_events WHERE field='status'").fetchone()[0],3)
        self.assertEqual(c.execute('SELECT initial_status_gap_seconds FROM issue_quality').fetchone()[0],10)
        self.assertEqual(c.execute('SELECT status_eligible FROM cohort_membership').fetchone()[0],1)

    def test_conflicting_status_quarantined_without_guessing(self):
        c=self.build([('status','waiting',10),('status','resolved',10),('status','closed',100)])
        self.assertEqual(c.execute('SELECT status_eligible FROM cohort_membership').fetchone()[0],0)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM observed_events WHERE field='status'").fetchone()[0],0)

    def test_cross_field_same_timestamp_is_not_conflict(self):
        c=self.build([('status','in_progress',10),('assignee','a',10),('status','closed',100)])
        self.assertEqual(c.execute('SELECT COUNT(*) FROM event_conflicts').fetchone()[0],0)

    def test_missing_time_quarantined(self):
        c=self.build([('status','in_progress',None),('status','closed',100)])
        self.assertEqual(c.execute('SELECT status_eligible FROM cohort_membership').fetchone()[0],0)

    def test_events_outside_bounds_and_final_mismatch(self):
        c=self.build([('status','open',-1),('status','resolved',101)])
        self.assertEqual(c.execute('SELECT events_before_creation,events_after_endpoint,final_status_mismatch FROM issue_quality').fetchone(),(1,1,1))
        self.assertEqual(c.execute('SELECT status_eligible FROM cohort_membership').fetchone()[0],0)

    def test_named_handoffs_exclude_initial_assignment_and_unassigned(self):
        c=self.build([('status','closed',100),('assignee','a',5),('assignee','',10),
                      ('assignee','b',15),('assignee','c',20)])
        self.assertEqual(c.execute('SELECT observed_named_handoffs,observed_assignment_blank_transitions FROM case_observed_measures').fetchone(),(1,2))

    def test_resolution_is_not_closed_or_first_resolved(self):
        c=self.build([('status','resolved',40),('status','closed',100)])
        self.assertEqual(c.execute('SELECT recorded_resolution_seconds,source_endpoint_seconds,first_resolved_state_seconds FROM case_observed_measures').fetchone(),(80,100,40))

    def test_identifier_normalization_is_exact(self):
        self.assertEqual(key('9007199254740993.0'),'9007199254740993')
        self.assertIsNone(key(''))
        with self.assertRaises(ValueError): key('1.5')

if __name__=='__main__':
    unittest.main()
