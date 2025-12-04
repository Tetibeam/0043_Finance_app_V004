import sys
import os
import pandas as pd
import json

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.utils.data_loader import get_df_from_db
from app.utils.db_manager import init_db
# Import the function to test
# We need to import it from the file. Since it's a private function (starts with _), we might need to import the module.
from app.routes import dashboard_service

def test_build_progress_rate():
    # Initialize DB
    init_db()
    
    table_columns = [
        "資産_実績_資産額", "資産_目標_資産額","資産_実績_トータルリターン", "資産_目標_トータルリターン", "資産_進捗率"
    ]
    try:
        print("Fetching data from DB...")
        df = get_df_from_db(
            table_name="category_cache_daily", index_col="date", columns_col=None,
            values_col=table_columns, aggfunc="sum", set_index=True
        )
        print("Data fetched. Shape:", df.shape)
        
        print("Testing _build_progress_rate...")
        # Access the private function
        json_str = dashboard_service._build_progress_rate(df)
        print("Result JSON length:", len(json_str))
        print("SUCCESS: _build_progress_rate executed without error.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_build_progress_rate()
