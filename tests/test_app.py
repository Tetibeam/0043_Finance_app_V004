import unittest
import sys
import os
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
import app.utils.db_manager as db_manager_module

class TestDashboardApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True
        
        # Patch db_manager to force sqlite
        self.original_db_type = db_manager_module.db_manager.db_type
        db_manager_module.db_manager.db_type = "sqlite"
        # Ensure sqlite config is initialized
        if not hasattr(db_manager_module.db_manager, 'finance_db'):
             base_dir = Path(__file__).resolve().parent.parent
             db_manager_module.db_manager._init_sqlite_config(base_dir)

    def tearDown(self):
        db_manager_module.db_manager.db_type = self.original_db_type

    def test_dashboard_view(self):
        """Test the dashboard HTML view"""
        response = self.client.get('/api/dashboard/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_dashboard_api_root(self):
        """Test the dashboard API root"""
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service'], 'dashboard')

    def test_dashboard_api_graphs(self):
        """Test the dashboard graphs API"""
        response = self.client.get('/api/dashboard/graphs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertIn('graphs', data)

    def test_dashboard_api_summary(self):
        """Test the dashboard summary API"""
        response = self.client.get('/api/dashboard/summary')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertIn('summary', data)

if __name__ == '__main__':
    unittest.main()
