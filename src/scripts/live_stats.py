from datetime import datetime, timedelta
import requests
import os
import psycopg2
from .scrape_live_games import scrape_today_games
from src.db import connect_supabase, close_connection_supabase


NBA_API = "http://rest.nbaapi.com/api"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
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
            year, month, day = d.year, d.month, d.day
            _, teams_played = scrape_today_games(day, month, year)
            print(f"Updating for {year}-{month}-{day}: {len(teams_played)} teams to update...")
            
            for team in teams_played:
                response = requests.get(f"{NBA_API}/playerdatatotals/query?season={year}&team={team}&pageSize=30")
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch data from API: {response.status_code}")
                data = response.json()
                if not data:
                    raise Exception("No data found in the API response")
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
                print(f"\tUpdated for {team}")

            missing_dates.append(d.strftime("%Y-%m-%d %H:%M:%S UTC"))
            d += timedelta(days=1)
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

