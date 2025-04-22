import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

def connect():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Database connection successful")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
def close_connection(conn):
    if conn:
        conn.close()
        print("Database connection closed")
    else:
        print("No connection to close")


def connect_supabase():
    return psycopg2.connect(SUPABASE_DB_URL)

def close_connection_supabase(conn):
    if conn:
        conn.close()
        print("Supabase Database connection closed")
    else:
        print("No supabase connection to close")

