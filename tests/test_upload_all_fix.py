import unittest
import os
import io
import pandas as pd
import tempfile
import sqlite3
from app import create_app
import app.utils.db_manager as db_manager_module
from pathlib import Path

class TestUploadAllFix(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Initialize tables expected by the app
        self.cursor.execute("CREATE TABLE asset (date TEXT, value INTEGER)")
        self.cursor.execute("CREATE TABLE balance (date TEXT, value INTEGER)")
        self.cursor.execute("CREATE TABLE target (date TEXT, value INTEGER)")
        self.conn.commit()
        self.conn.close()

        # Configure app to use the temp db
        self.app = create_app()
        self.app.config['DATABASE'] = {
            'sqlite': {
                'path': os.path.dirname(self.db_path),
                'finance': os.path.basename(self.db_path)
            }
        }
        self.app.testing = True
        self.client = self.app.test_client()

        # Patch db_manager to use temp sqlite db
        self.original_db_type = db_manager_module.db_manager.db_type
        self.original_finance_db = getattr(db_manager_module.db_manager, 'finance_db', None)
        
        db_manager_module.db_manager.db_type = "sqlite"
        db_manager_module.db_manager.finance_db = Path(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.remove(self.db_path)
        except OSError:
            pass
        
        # Restore db_manager
        db_manager_module.db_manager.db_type = self.original_db_type
        if self.original_finance_db:
            db_manager_module.db_manager.finance_db = self.original_finance_db

    def test_upload_all_success(self):
        # Create dummy Parquet files
        df_asset = pd.DataFrame({'date': ['2023-01-01'], 'value': [100]})
        df_balance = pd.DataFrame({'date': ['2023-01-01'], 'value': [200]})
        df_target = pd.DataFrame({'date': ['2023-01-01'], 'value': [300]})

        asset_parquet = io.BytesIO()
        df_asset.to_parquet(asset_parquet)
        asset_parquet.seek(0)

        balance_parquet = io.BytesIO()
        df_balance.to_parquet(balance_parquet)
        balance_parquet.seek(0)

        target_parquet = io.BytesIO()
        df_target.to_parquet(target_parquet)
        target_parquet.seek(0)

        data = {
            'file_asset': (asset_parquet, 'asset.parquet'),
            'file_balance': (balance_parquet, 'balance.parquet'),
            'file_target': (target_parquet, 'target.parquet')
        }

        response = self.client.post(
            '/api/data/upload_all',
            data=data
        )

        # If the bug exists, this will be 500
        self.assertEqual(response.status_code, 200, f"Response was: {response.data.decode('utf-8')}")
        self.assertIn(b"success", response.data)

if __name__ == '__main__':
    unittest.main()
