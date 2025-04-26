from .setup_db import connect_supabase, close_connection_supabase

def create_tables():
    conn = connect_supabase()
    if conn:
        cursor = conn.cursor()
        with open("src/db/sql/create_tables.sql", "r") as f:
            cursor.execute(f.read())
        conn.commit()
        cursor.close()
        close_connection_supabase(conn)
        print("Tables created successfully")
    else:
        print("Failed to create tables: No connection to database")

create_tables()