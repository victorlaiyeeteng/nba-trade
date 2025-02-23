import psycopg2
from src.db import connect, close_connection


def load_team_stats(team_data, year):
    conn = connect()

    if conn:
        cursor = conn.cursor()
        for team, stats in team_data.items():
            wins, losses, rank = stats
            winpercent = round(wins / (wins + losses), 3) if (wins + losses) > 0 else 0
            insert_query = f"INSERT INTO team_stats (team, season, wins, losses, winpercent, rank) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (team, year, wins, losses, winpercent, rank)
            try:
                cursor.execute(insert_query, values)
            except psycopg2.Error as e:
                print(f"Error inserting data for team {team}: {e}")
                return
        conn.commit()
        cursor.close()
        close_connection(conn)
        print(f"Team stats loaded successfully for year {year}")
    else:
        print("Failed to load team stats: No connection to database")


team_data = {
    "LAL": [52, 19, 1],  # 1st in the West
    "LAC": [49, 23, 2],  # 2nd in the West
    "DEN": [46, 27, 3],  # 3rd in the West
    "HOU": [44, 28, 4],  # 4th in the West
    "OKC": [44, 28, 5],  # 5th in the West
    "UTA": [44, 28, 6],  # 6th in the West
    "DAL": [43, 32, 7],  # 7th in the West
    "POR": [35, 39, 8],  # 8th in the West
    "MEM": [34, 39, 9],  # 9th in the West
    "PHO": [34, 39, 10],  # 10th in the West
    "SAS": [32, 39, 11],  # 11th in the West
    "SAC": [31, 41, 12],  # 13th in the West
    "NOP": [30, 42, 13],  # 12th in the West
    "MIN": [19, 45, 14],  # 14th in the West
    "GSW": [15, 50, 15],  # 15th in the West

    "MIL": [56, 17, 1],  # 1st in the East
    "TOR": [53, 19, 2],  # 2nd in the East
    "BOS": [48, 24, 3],  # 3rd in the East
    "MIA": [44, 29, 4],  # 4th in the East
    "IND": [45, 28, 5],  # 5th in the East
    "PHI": [43, 30, 6],  # 6th in the East
    "BRK": [35, 37, 7],  # 7th in the East
    "ORL": [33, 40, 8],  # 8th in the East
    "WAS": [25, 47, 9],  # 9th in the East
    "CHI": [22, 43, 10],  # 10th in the East
    "DET": [20, 46, 11],  # 11th in the East
    "CLE": [19, 46, 12],  # 12th in the East
    "ATL": [20, 47, 13],  # 13th in the East
    "CHO": [23, 42, 14],  # 14th in the East
    "NYK": [21, 45, 15]
}

# load_team_stats(team_data, 2020)