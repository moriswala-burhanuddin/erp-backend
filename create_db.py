
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # CONNECT TO DEFAULT POSTGRES DB TO CREATE NEW DB
    try:
        # Connect using user-provided credentials
        print("Attempting to connect to PostgreSQL...")
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='admin', port='5432')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if db exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'storeflow_db'")
        exists = cur.fetchone()
        
        if not exists:
            print("Creating database 'storeflow_db'...")
            cur.execute('CREATE DATABASE storeflow_db')
            print("Database created successfully!")
        else:
            print("Database 'storeflow_db' already exists.")
            
        cur.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"CONNECTION FAILED: {e}")
        return False

if __name__ == "__main__":
    create_database()
