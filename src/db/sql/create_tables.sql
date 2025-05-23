CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER,
    playerName TEXT,
    position TEXT,
    age INTEGER,
    games INTEGER,
    gamesStarted INTEGER,
    minutesPg REAL,
    fieldGoals INTEGER,
    fieldAttempts INTEGER,
    fieldPercent REAL,
    threeFg INTEGER,
    threeAttempts INTEGER,
    threePercent REAL,
    twoFg INTEGER,
    twoAttempts INTEGER,
    twoPercent REAL,
    effectFgPercent REAL,
    ft INTEGER,
    ftAttempts INTEGER,
    ftPercent REAL,
    offensiveRb INTEGER,
    defensiveRb INTEGER,
    totalRb INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personalFouls INTEGER,
    points INTEGER,
    team TEXT,
    season INTEGER,
    playerId TEXT,
    PRIMARY KEY (playerId, season)
);

CREATE TABLE IF NOT EXISTS trade_outcome (
    playerId TEXT, 
    season INTEGER, 
    outcome INTEGER, 
    PRIMARY KEY (playerId, season), 
    FOREIGN KEY (playerId, season) REFERENCES player_stats(playerId, season)
);

CREATE TABLE IF NOT EXISTS player_stats_vectorized (
    playerid TEXT,
    season INTEGER,
    stat_vector vector(27), -- 27 features
    PRIMARY KEY (playerId, season),
    FOREIGN KEY (playerId, season) REFERENCES player_stats(playerId, season) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    team TEXT,
    season INTEGER,
    wins INTEGER, 
    losses INTEGER, 
    winPercent REAL, 
    rank INTEGER
);