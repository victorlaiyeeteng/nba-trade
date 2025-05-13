

async def fetch_player_stats(database, playerid, season):
    get_player_stat_query = """
    SELECT * FROM player_stats
    WHERE playerid = :playerid and season = :season;
    """
    return await database.fetch_one(query=get_player_stat_query, values={"playerid": playerid, "season": season})
    
async def fetch_player_vector(database, playerid, season):
    get_player_stat_vectorized_query = """
    SELECT stat_vector FROM player_stats_vectorized
    WHERE playerid = :playerid AND season = :season;
    """
    return await database.fetch_one(query=get_player_stat_vectorized_query, values={"playerid": playerid, "season": season})

async def fetch_similar_players(database, playerid, player_vector, top_k):
    get_similar_players = """
    SELECT playerid, season, 1 - (stat_vector <=> :player_vector) AS similarity
    FROM player_stats_vectorized
    WHERE playerid != :playerid
    ORDER BY stat_vector <=> :player_vector
    LIMIT :top_k
    """

    similar_players = await database.fetch_all(
        query=get_similar_players, 
        values={"playerid": playerid, "player_vector": player_vector, "top_k": top_k}
    )
    
    player_ids = [player["playerid"] for player in similar_players]
    if not player_ids:
        return []

    get_player_names = """
    SELECT DISTINCT playerid, playername
    FROM player_stats
    WHERE playerid = ANY(:player_ids)
    """
    
    player_names = await database.fetch_all(
        query=get_player_names, 
        values={"player_ids": player_ids}
    )

    player_name_map = {player["playerid"]: player["playername"] for player in player_names}

    similar_players_dicts = [dict(player) for player in similar_players]
    for player in similar_players_dicts:
        player["playername"] = player_name_map.get(player["playerid"], None)
    
    return similar_players_dicts

async def fetch_player_by_name(database, sub_name, season):
    search_query = """
    SELECT DISTINCT playerid, playername, team, season
    FROM player_stats
    WHERE LOWER(playername) LIKE LOWER(:query)
    AND season = :season
    LIMIT 5;
    """
    return await database.fetch_all(
        query=search_query, 
        values={"query": f"%{sub_name.lower()}%", "season": season}
    )