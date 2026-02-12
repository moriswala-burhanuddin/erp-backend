
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, '../electron/storeflow.db')

def verify_sync_flags():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("--- SYNC FLAG VERIFICATION ---")
    
    # 1. Simulate a User addition (already fixed in db.cjs, but let's check current state)
    cur.execute("INSERT OR REPLACE INTO users (id, name, email, role, store_id, updated_at, sync_status) VALUES ('test-user-sync-1', 'Test Sync User', 'test@sync.com', 'user', 'store-1', datetime('now'), 0)")
    
    # 2. Simulate an Account Balance update (the core fix)
    cur.execute("UPDATE accounts SET balance = balance + 100, sync_status = 0 WHERE id = 'acc-1'")
    
    conn.commit()
    
    # 3. Check what is dirty
    tables = ['users', 'accounts', 'products', 'sales']
    for table in tables:
        cur.execute(f"SELECT COUNT(*) as count FROM {table} WHERE sync_status = 0")
        count = cur.fetchone()['count']
        print(f"Table {table}: {count} dirty records")
        
    conn.close()

if __name__ == "__main__":
    verify_sync_flags()
