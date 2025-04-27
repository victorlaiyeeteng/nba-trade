from src.db import connect_supabase, close_connection_supabase

def find_similar_players(playerid, season, top_k=5):
    conn = connect_supabase()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT stat_vector
            FROM player_stats_vectorized
            WHERE playerid = %s AND season = %s
        """, (playerid, season))

        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Player {playerid} for season {season} not found.")
        
        player_vector = result[0]
        cursor.execute("""
            SELECT playerid, season, 1 - (stat_vector <=> %s) AS similarity
            FROM player_stats_vectorized
            WHERE playerid != %s AND season = %s
            ORDER BY stat_vector <=> %s
            LIMIT %s
        """, (player_vector, playerid, season, player_vector, top_k))

        similar_players = cursor.fetchall()
        cursor.close()
        close_connection_supabase(conn)

        return [
            {
                'playerid': row[0], 
                'season': row[1], 
                'similarity_percentage': round(row[2] * 100, 2)
            }
            for row in similar_players
        ]

    else:
        print("Failed to perform statline similarity search: No connection to database")

print(find_similar_players("butleji01", 2025))

