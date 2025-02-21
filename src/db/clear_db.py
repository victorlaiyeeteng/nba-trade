from db.setup_db import connect, close_connection

def clear_tables():
    conn = connect()
    if conn:
        cursor = conn.cursor()
        with open("src/db/sql/delete_tables.sql", "r") as f:
            cursor.execute(f.read())
        conn.commit()
        cursor.close()
        close_connection(conn)
        print("Tables deleted successfully")
    else:
        print("Failed to clear tables: No connection to database")

clear_tables()