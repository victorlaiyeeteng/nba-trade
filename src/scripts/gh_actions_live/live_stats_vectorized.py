import psycopg2
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from src.db import connect_supabase, close_connection_supabase

positions_int_map = {"PG": 0, "SG": 1, "SF": 2, "PF": 3, "C": 4}

conn = connect_supabase()

if conn:
    cursor = conn.cursor()
    get_player_stats_query = """SELECT
    position,age,games,gamesStarted,minutesPg,fieldGoals,fieldAttempts,fieldPercent,
    threeFg,threeAttempts,threePercent,twoFg,twoAttempts,twoPercent,effectFgPercent,
    ft,ftAttempts,ftPercent,offensiveRb,defensiveRb,totalRb,assists,
    steals,blocks,turnovers,personalFouls,points,
    season,playerId FROM player_stats
    """
    cursor.execute(get_player_stats_query)
    rows = cursor.fetchall()
    feature_columns = [
    "position","age","games","gamesStarted","minutesPg","fieldGoals","fieldAttempts","fieldPercent",
    "threeFg","threeAttempts","threePercent","twoFg","twoAttempts","twoPercent","effectFgPercent",
    "ft","ftAttempts","ftPercent","offensiveRb","defensiveRb","totalRb","assists",
    "steals","blocks","turnovers","personalFouls","points"
    ]
    
    df = pd.DataFrame(rows, columns=feature_columns + ["season", "playerId"])
    df['position'] = df['position'].apply(lambda x: positions_int_map[x])
    for col in feature_columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mean())

    features = df[feature_columns].values
    scaler = StandardScaler()
    standardized_features = scaler.fit_transform(features)
    print(f"Starting adding/updating statline vectors for {df.shape[0]} players")
    total_players_count = df.shape[0]
    players_count = 0

    for i, row in df.iterrows():
        playerid = row['playerId']
        season = row['season']
        vector = standardized_features[i].tolist()
        try:
            cursor.execute("""
                INSERT INTO player_stats_vectorized (playerId, season, stat_vector)
                VALUES (%s, %s, %s)
                ON CONFLICT (playerId, season)
                DO UPDATE SET stat_vector = EXCLUDED.stat_vector
            """, (playerid, season, vector))
            players_count += 1
            print(f"Successfully added/updated for {players_count}/{total_players_count} players...")
        except:
            print(f"Error adding vector for {playerid}")
            break

    conn.commit()
    cursor.close()
    print(f"Successfully completed adding vectorized statline for {players_count} players!")
    close_connection_supabase(conn)
else:
    print("Failed to vectorize player stats: No connection to database")
