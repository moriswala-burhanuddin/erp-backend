
import psycopg2

def list_tables():
    try:
        conn = psycopg2.connect(dbname='storeflow_db', user='postgres', host='localhost', password='admin', port='5432')
        cur = conn.cursor()
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        rows = cur.fetchall()
        print("Tables in 'public' schema:")
        for row in rows:
            print(f"- {row[0]}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
