import os
import psycopg2
from dotenv import load_dotenv
from src.db import connect, close_connection
import requests

load_dotenv()

NBA_PLAYER_API = os.getenv("NBA_PLAYER_STATS_API_ENDPOINT")

def load_player_historical_stats(year):
    response = requests.get(f"{NBA_PLAYER_API}/playerdatatotals/query?season={year}&pageSize=600")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")
    data = response.json()
    if not data:
        raise Exception("No data found in the API response")
    
    conn = connect()
    if conn:
        cursor = conn.cursor()
        for player in data:
            columns = ", ".join(player.keys())
            team = player.get("team")
            if team == "TOT" or team == "2TM" or team == "3TM":
                continue
            insert_query = "INSERT INTO player_stats ({}) VALUES ({}) ON CONFLICT (playerId, season) DO UPDATE SET {}".format(
                    columns,
                    ", ".join(["%s"] * len(player)), 
                    ", ".join([f"{key} = EXCLUDED.{key}" for key in player.keys()])
                )
            values = tuple(player.values())
            try:
                cursor.execute(insert_query, values)
            except psycopg2.Error as e:
                print(f"Error inserting data for player {player.get('player_id')}: {e}")

        conn.commit()
        cursor.close()
        close_connection(conn)
        print(f"Player historical stats loaded successfully for year {year}")
        
    else:
        print("Failed to load player historical stats: No connection to database")

def load_player_historical_advanced_stats(year):
    response = requests.get(f"{NBA_PLAYER_API}/playerdataadvanced/query?season={year}&pageSize=600")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")
    data = response.json()
    if not data:
        raise Exception("No data found in the API response")
    
    conn = connect()
    if conn:
        cursor = conn.cursor()
        for player in data:
            player_id = player.get("playerId")
            team = player.get("team")
            if team == "TOT" or team == "2TM" or team == "3TM":
                continue
            set_clause = ", ".join([f"{key} = %s" for key in player.keys()])
            update_query = f"UPDATE player_stats SET {set_clause} WHERE playerid = %s AND season = %s AND team = %s"
            values = tuple(player.values()) + (player_id, year, team)

            try:
                cursor.execute(update_query, values)
            except psycopg2.Error as e:
                print(f"Error updating data for player {player.get('playerId')}: {e}")
                return

        conn.commit()
        cursor.close()
        close_connection(conn)
        print(f"Player historical advanced stats added successfully for year {year}")
        
    else:
        print("Failed to load player historical advanced stats: No connection to database")

# Outcome = 0 (waived), 1 (same team), 2 (traded)
def load_player_end_of_season_outcome():
    conn = connect()
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
        close_connection(conn)
        print(f"Player end of season outcome updated successfully")
    else:
        print("Failed to load player end of season outcome: No connection to database")

for year in range(2020, 2026):
    load_player_historical_stats(year)
    load_player_historical_advanced_stats(year)
# load_player_end_of_season_outcome()

# response = requests.get(f"{NBA_PLAYER_API}/playerdatatotals/query?season=2021&pageSize=600")
# if response.status_code != 200:
#     raise Exception(f"Failed to fetch data from API: {response.status_code}")
# data = response.json()
# total = 0
# qualified_teams = 0
# for player in data:
#     total += 1
#     if player.get("team")   == "TOT" or player.get("team") == "2TM":
#         continue
#     qualified_teams += 1
# print(total, qualified_teams)


