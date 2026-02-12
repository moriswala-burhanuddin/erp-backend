
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def recreate_database():
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='admin', port='5432')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Terminating other sessions on 'storeflow_db'...")
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'storeflow_db'
              AND pid <> pg_backend_pid();
        """)
        
        print("Dropping database 'storeflow_db'...")
        try:
            cur.execute("DROP DATABASE storeflow_db")
            print("Database dropped.")
        except Exception as e:
            print(f"Drop error (maybe it doesn't exist): {e}")
            
        print("Creating database 'storeflow_db'...")
        cur.execute("CREATE DATABASE storeflow_db")
        print("Database created successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Connection/Creation error: {e}")

if __name__ == "__main__":
    recreate_database()
