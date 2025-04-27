import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from src.db import connect_supabase, close_connection_supabase

positions_int_map = {"PG": 0, "SG": 1, "SF": 2, "PF": 3, "C": 4}
feature_columns = [
    "position", "age", "games", "gamesStarted", "minutesPg", "fieldGoals", "fieldAttempts", "fieldPercent",
    "threeFg", "threeAttempts", "threePercent", "twoFg", "twoAttempts", "twoPercent", "effectFgPercent",
    "ft", "ftAttempts", "ftPercent", "offensiveRb", "defensiveRb", "totalRb", "assists",
    "steals", "blocks", "turnovers", "personalFouls", "points"
]

def preprocess_player_stats(df):
    """ Preprocess the player stats DataFrame before scaling """
    df['position'] = df['position'].apply(lambda x: positions_int_map[x.split('-')[0]] if x else np.nan)
    for col in feature_columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mean())
    return df

def fit_scaler_and_save(df, scaler_path="scaler_params.pkl"):
    """ Fit a StandardScaler and save mean/scale to file """
    scaler = StandardScaler()
    features = df[feature_columns].values
    scaler.fit(features)
    
    with open(scaler_path, "wb") as f:
        pickle.dump({'mean': scaler.mean_, 'scale': scaler.scale_}, f)
    print(f"Scaler parameters saved to {scaler_path}")
    return scaler.mean_, scaler.scale_

def vectorize_player_stats(df, mean, scale):
    """ Vectorize a DataFrame using provided mean and scale """
    features = df[feature_columns].values
    standardized_features = (features - mean) / scale
    return standardized_features

def main_vectorize_player_stats():
    conn = connect_supabase()
    if not conn:
        print("Failed to connect to DB.")
        return
    
    cursor = conn.cursor()
    query = """SELECT
        position, age, games, gamesStarted, minutesPg, fieldGoals, fieldAttempts, fieldPercent,
        threeFg, threeAttempts, threePercent, twoFg, twoAttempts, twoPercent, effectFgPercent,
        ft, ftAttempts, ftPercent, offensiveRb, defensiveRb, totalRb, assists,
        steals, blocks, turnovers, personalFouls, points,
        season, playerId FROM player_stats
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=feature_columns + ["season", "playerId"])

    df = preprocess_player_stats(df)
    mean, scale = fit_scaler_and_save(df) 

    vectors = vectorize_player_stats(df, mean, scale)

    print(f"Starting adding/updating statline vectors for {df.shape[0]} players")
    player_count = 0
    for i, row in df.iterrows():
        playerid = row['playerId']
        season = row['season']
        vector = vectors[i].tolist()
        try:
            cursor.execute("""
                INSERT INTO player_stats_vectorized (playerId, season, stat_vector)
                VALUES (%s, %s, %s)
                ON CONFLICT (playerId, season)
                DO UPDATE SET stat_vector = EXCLUDED.stat_vector
            """, (playerid, season, vector))
            player_count += 1
            print(f"Successfully added/updated statline vector for player {player_count}")
        except Exception as e:
            print(f"Error adding vector for player {playerid}: {e}")
            continue

    conn.commit()
    cursor.close()
    close_connection_supabase(conn)
    print(f"Successfully completed adding vectorized statlines!")

if __name__ == "__main__":
    main_vectorize_player_stats()
