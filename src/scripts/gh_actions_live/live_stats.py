from datetime import datetime, timedelta
import pickle
import requests
import pandas as pd
import os
import psycopg2
from ..scrape_live_games import scrape_today_games
from src.db import connect_supabase, close_connection_supabase
from src.scripts.player_stats_vectorized import preprocess_player_stats, vectorize_player_stats, feature_columns

def get_dates(d):
    year, month, day = d.year, d.month, d.day
    if month >= 10:
        season = year + 1
    else: 
        season = year
    return year, month, day, season


NBA_API = "http://rest.nbaapi.com/api"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
last_update_date_file_path = os.path.join(project_root, "logs", "stats_last_update.txt")
os.makedirs(os.path.dirname(last_update_date_file_path), exist_ok=True)

with open(last_update_date_file_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]
    latest_date_str = lines[-1]

latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d %H:%M:%S UTC")
regular_season_cutoff_date = datetime.strptime("2025-04-19 11:00:00 UTC", "%Y-%m-%d %H:%M:%S UTC")
current_date = datetime.utcnow().replace(hour=11, minute=0, second=0, microsecond=0)

missing_dates = []
d = latest_date + timedelta(days=1)
conn = False
if d <= min(regular_season_cutoff_date, current_date):
    conn = connect_supabase()
    if conn:
        cursor = conn.cursor()
        print("Successfully connected to Supabase DB")
        while d <= min(regular_season_cutoff_date, current_date):
            year, month, day, season = get_dates(d)
            response = requests.get(f"{NBA_API}/playerdatatotals/query?season={year}&pageSize=1000")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data from API: {response.status_code}")
            data = response.json()
            if not data:
                raise Exception("No data found in the API response")
            data.sort(key=lambda x: x['id'])

            print(f"Updating for {year}-{month}-{day}: {len(data)} players to update...")

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

            missing_dates.append(d.strftime("%Y-%m-%d %H:%M:%S UTC"))
            d += timedelta(days=1)
        
        print(f"Completed updating player regular stats (total: {len(data)})")

        _, _, _, season = get_dates(d)
        with open("scaler_params.pkl", "rb") as f:
            scaler_params = pickle.load(f)
        mean = scaler_params['mean']
        scale = scaler_params['scale']
        query = """SELECT
            position, age, games, gamesStarted, minutesPg, fieldGoals, fieldAttempts, fieldPercent,
            threeFg, threeAttempts, threePercent, twoFg, twoAttempts, twoPercent, effectFgPercent,
            ft, ftAttempts, ftPercent, offensiveRb, defensiveRb, totalRb, assists,
            steals, blocks, turnovers, personalFouls, points,
            season, playerId FROM player_stats WHERE season={}
        """.format(season)
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=feature_columns + ["season", "playerId"])
        df = preprocess_player_stats(df)
        vectors = vectorize_player_stats(df, mean, scale)
        for i, row in df.iterrows():
            playerid = row['playerId']
            season = row['season']
            vector = vectors[i].tolist()
            cursor.execute("""
                INSERT INTO player_stats_vectorized (playerId, season, stat_vector)
                VALUES (%s, %s, %s)
                ON CONFLICT (playerId, season)
                DO UPDATE SET stat_vector = EXCLUDED.stat_vector
            """, (playerid, season, vector))
        print(f"Completed updating player statline vectors (total: {df.shape[0]})")

        conn.commit()
        cursor.close()
        close_connection_supabase(conn)
    else:
        print("Failed to connect to Supabase DB")
    print(f"Completed updating player stats till {missing_dates[-1]}")
else:
    print("Stats are all up to date (end of regular season)")

if missing_dates:
    with open(last_update_date_file_path, "w") as f:
        f.write(missing_dates[-1])

