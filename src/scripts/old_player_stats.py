import os
import psycopg2
from dotenv import load_dotenv
from src.db import connect_supabase, close_connection_supabase
import requests

load_dotenv()

NBA_PLAYER_API = os.getenv("NBA_PLAYER_STATS_API_ENDPOINT")

def load_player_historical_stats(year):
    response = requests.get(f"{NBA_PLAYER_API}/playerdatatotals/query?season={year}&sortBy=id&ascending=true&pageSize=700")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")
    data = response.json()
    if not data:
        raise Exception("No data found in the API response")
    
    data.sort(key=lambda x: x['id'])
    conn = connect_supabase()
    if conn:
        cursor = conn.cursor()
        for player in data:
            columns = ", ".join(player.keys())
            team = player.get("team")
            values = tuple(player.values())
            insert_query = f"""
                INSERT INTO player_stats ({columns})
                VALUES ({", ".join(['%s'] * len(player))})
                ON CONFLICT (playerid, season) DO UPDATE SET
            """
            if team in ["TOT", "2TM", "3TM"]:
                update_clause = ", ".join([f"{key} = EXCLUDED.{key}" for key in player.keys()])
            else:
                update_clause = "team = EXCLUDED.team"
            insert_query += update_clause

            try:
                cursor.execute(insert_query, values)
            except psycopg2.Error as e:
                print(f"Error inserting data for player {player.get('player_id')}: {e}")

        conn.commit()
        cursor.close()
        close_connection_supabase(conn)
        print(f"Player historical stats loaded successfully for year {year}")
        
    else:
        print("Failed to load player historical stats: No connection to database")

# Outcome = 0 (waived), 1 (same team), 2 (traded)
def load_player_end_of_season_outcome():
    conn = connect_supabase()
    if conn:
        cursor = conn.cursor()
        update_query = f"""
            UPDATE player_stats ps1
            SET outcome = CASE
                WHEN NOT EXISTS (SELECT 1 FROM player_stats ps2 WHERE ps1.playerid = ps2.playerid AND ps2.season = ps1.season + 1) THEN 0
                WHEN ps1.team = (SELECT team FROM player_stats ps2 WHERE ps1.playerid = ps2.playerid AND ps2.season = ps1.season + 1) THEN 1
                ELSE 2
            END
        """
        try:
            cursor.execute(update_query)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error updating player end of season outcome: {e}")
            return
        cursor.close()
        close_connection_supabase(conn)
        print(f"Player end of season outcome updated successfully")
    else:
        print("Failed to load player end of season outcome: No connection to database")

for year in range(2020, 2026):
    load_player_historical_stats(year)


# load_player_end_of_season_outcome()


# team -> 2TM -> team -> 3TM -> team
# TOT -> team -> team
