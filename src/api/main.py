from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.db_functions import fetch_player_stats, fetch_player_vector, fetch_similar_players, fetch_player_by_name
from src.db import connect_supabase_with_fastapi, disconnect_supabase_with_fastapi
from src.db.setup_db import database

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
    await connect_supabase_with_fastapi()

@app.on_event("shutdown")
async def disconnect_from_db():
    await disconnect_supabase_with_fastapi()

@app.get("/player_stats")
async def get_player_stats(playerid: str, season: int, top_k: int = 5):
    player_stat_results = await fetch_player_stats(database, playerid, season)
    player_stat_vectorized_results = await fetch_player_vector(database, playerid, season)
    if player_stat_vectorized_results is None:
        return {"error": "Stat vector not found for this player and season."}
    player_vector = player_stat_vectorized_results['stat_vector']
    similar_player_results = await fetch_similar_players(database, playerid, player_vector, top_k)

    return {
        "playerid": playerid,
        "season": season, 
        "player_stats": player_stat_results, 
        "similar_players": similar_player_results
    }

@app.get("/search_players")
async def search_players(query: str, season: int):
    results = await fetch_player_by_name(database, query, season)
    return [dict(row) for row in results]

@app.get("/ping")
async def ping():
    return {"message": "pong"}
