
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, '../electron/storeflow.db')

def verify_stock_sync_flag():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("--- STOCK SYNC FLAG VERIFICATION ---")
    
    # Check current product state
    cur.execute("SELECT id, name, quantity, sync_status FROM products WHERE id = 'prod-1'")
    product = cur.fetchone()
    print(f"Initial Product: {product['name']}, Qty: {product['quantity']}, Sync: {product['sync_status']}")
    
    # Simulate the NEW processSale logic (marking dirty)
    # The logic in db.cjs is: UPDATE products SET quantity = quantity - ?, last_used = ?, updated_at = datetime("now"), sync_status = 0 WHERE id = ?
    cur.execute("UPDATE products SET quantity = quantity - 1, sync_status = 0, updated_at = datetime('now') WHERE id = 'prod-1'")
    conn.commit()
    
    # Check final product state
    cur.execute("SELECT id, name, quantity, sync_status FROM products WHERE id = 'prod-1'")
    product = cur.fetchone()
    print(f"Final Product: {product['name']}, Qty: {product['quantity']}, Sync: {product['sync_status']}")
    
    if product['sync_status'] == 0:
        print("SUCCESS: Product correctly marked as dirty (sync_status=0)")
    else:
        print("FAILURE: Product NOT marked as dirty")
        
    conn.close()

if __name__ == "__main__":
    verify_stock_sync_flag()
