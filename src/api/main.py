from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import databases

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_DB_URL")
database = databases.Database(SUPABASE_URL)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def connect_to_db():
    await database.connect()

@app.on_event("shutdown")
async def disconnect_from_db():
    await database.disconnect()

@app.get("/player_stats")
async def get_player_stats(playerid: str, season: int, top_k: int = 5):
    get_player_stat_query = """
    SELECT * FROM player_stats
    WHERE playerid = :playerid and season = :season;
    """
    player_stat_results = await database.fetch_all(query=get_player_stat_query, values={"playerid": playerid, "season": season})
    
    get_player_stat_vectorized_query = """
    SELECT stat_vector FROM player_stats_vectorized
    WHERE playerid = :playerid AND season = :season;
    """
    player_stat_vectorized_results = await database.fetch_one(query=get_player_stat_vectorized_query, values={"playerid": playerid, "season": season})
    if player_stat_vectorized_results is None:
        return {"error": "Stat vector not found for this player and season."}
    player_vector = player_stat_vectorized_results['stat_vector']

    get_similar_players = """
    SELECT playerid, season, 1 - (stat_vector <=> :player_vector) AS similarity
    FROM player_stats_vectorized
    WHERE playerid != :playerid
    ORDER BY stat_vector <=> :player_vector
    LIMIT :top_k
    """
    similar_player_results = await database.fetch_all(
        query=get_similar_players, 
        values={"playerid": playerid, "player_vector": player_vector, "top_k": top_k})

    return {
        "playerid": playerid,
        "season": season, 
        "player_stats": player_stat_results, 
        "similar_players": similar_player_results
    }

@app.get("/search_players")
async def search_players(query: str, season: int):
    search_query = """
    SELECT DISTINCT playerid, playername, team, season
    FROM player_stats
    WHERE LOWER(playername) LIKE LOWER(:query)
    AND season = :season
    LIMIT 5;
    """
    results = await database.fetch_all(
        query=search_query, 
        values={"query": query, "season": season}
    )
    return [dict(row) for row in results]
