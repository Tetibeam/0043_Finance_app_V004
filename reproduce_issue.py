import sys
import os
import pandas as pd
import json
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

from app.utils.db_manager import init_db
from app.routes.Allocation_Matrix_service import build_dashboard_payload, _read_table_from_db, _build_liquidity_horizon

def test():
    # Init DB
    print("Initializing DB...")
    init_db(os.getcwd())
    
    # Run the function
    print("Running build_dashboard_payload...")
    try:
        # We can just call build_dashboard_payload which calls everything
        payload = build_dashboard_payload(include_graphs=True, include_summary=False)
        print("Success! Payload generated.")
        # Optional: check if the 'liquidity_horizon' is in graphs
        if "graphs" in payload and "liquidity_horizon" in payload["graphs"]:
            print("Liquidity horizon graph present.")
        else:
            print("Liquidity horizon graph MISSING.")
            
    except Exception as e:
        print(f"Caught exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test()
