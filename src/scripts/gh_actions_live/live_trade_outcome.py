from src.db import connect_supabase, close_connection_supabase

conn = connect_supabase()
if conn:
    cursor = conn.cursor()

    # Get current season (should not be included in trade_outcome table)
    latest_season_ps_query = "SELECT MAX(season) from player_stats"
    cursor.execute(latest_season_ps_query)
    latest_season_ps = cursor.fetchone()[0]

    # Insert players from latest season completed
    latest_season_to_query = "SELECT MAX(season) from trade_outcome"
    cursor.execute(latest_season_to_query)
    latest_season_to = cursor.fetchone()[0]
    if latest_season_ps - latest_season_to > 1:
        print(f"Adding players from latest season completed - {latest_season_ps - 1}")
        insert_players_query = """
            INSERT INTO trade_outcome (playerId, season)
            SELECT ps.playerId, ps.season
            FROM player_stats ps WHERE ps.season = {}
        """.format(latest_season_ps - 1)
        cursor.execute(insert_players_query)

    # Update player trade outcome - 0 (waived), 1 (same team), 2 (traded)
    update_outcome_query = """
        UPDATE trade_outcome to1
        SET outcome = CASE
            WHEN NOT EXISTS (SELECT 1 FROM player_stats ps1 WHERE to1.playerid = ps1.playerid AND ps1.season = to1.season + 1) THEN 0
            WHEN EXISTS (
                SELECT 1
                FROM player_stats ps_current
                JOIN player_stats ps_next
                ON ps_current.playerId = ps_next.playerId
                AND ps_current.team = ps_next.team
                AND ps_current.season + 1 = ps_next.season
                WHERE ps_current.playerId = to1.playerId
                AND ps_current.season = to1.season
            ) THEN 1
            ELSE 2
        END
        WHERE to1.season = {}
    """.format(latest_season_ps - 1)
    cursor.execute(update_outcome_query)
    print(f"Updating trade outcome for season {latest_season_ps - 1} complete.")


    conn.commit()
    cursor.close()
    close_connection_supabase(conn)
else:
    print("Failed to update trade outcomes: No connection to database")

