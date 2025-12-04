import unittest
import pandas as pd
import os
import sqlite3
import tempfile
from app.utils.data_loader import append_to_table
from app.utils.db_manager import init_db
from pathlib import Path

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        # Initialize db_manager
        init_db()
        
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE test_table (col1 INTEGER, col2 TEXT)")
        self.conn.commit()
        self.conn.commit()
        self.conn.close()

        # Patch db_manager to use temp sqlite db
        from app.utils.db_manager import db_manager
        self.original_db_type = db_manager.db_type
        self.original_finance_db = getattr(db_manager, 'finance_db', None)
        
        db_manager.db_type = "sqlite"
        db_manager.finance_db = Path(self.db_path)

    def tearDown(self):
        from app.utils.db_manager import db_manager
        
        os.close(self.db_fd)
        try:
            os.remove(self.db_path)
        except OSError:
            pass
        
        # Restore db_manager
        db_manager.db_type = self.original_db_type
        if self.original_finance_db:
            db_manager.finance_db = self.original_finance_db

    def test_append_to_table(self):
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        # This should fail if Path is not imported
        added = append_to_table(df, 'test_table')
        self.assertEqual(added, 2)
        
        # Verify data
        with sqlite3.connect(self.db_path) as conn:
            df_read = pd.read_sql_query("SELECT * FROM test_table", conn)
        self.assertEqual(len(df_read), 2)

if __name__ == '__main__':
    unittest.main()
