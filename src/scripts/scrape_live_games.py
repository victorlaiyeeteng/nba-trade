import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date



basketball_reference_url = "https://www.basketball-reference.com"

def scrape_today_games(day=None, month=None, year=None):
    if day is None or month is None or year is None:
        today_date = date.today()
        day, month, year = today_date.day, today_date.month, today_date.year
    response = requests.get(f"{basketball_reference_url}/boxscores/?month={month}&day={day}&year={year}")
    soup = BeautifulSoup(response.content, 'html.parser')

    games_container = soup.find('div', class_="game_summaries")
    if games_container is None:
        return f"No games on {day}-{month}-{year}"
    games_data = []
    all_teams_played = set()
    for game in games_container.find_all('div', class_="game_summary"):
        teams_table = game.find('table', class_='teams')
        rows = teams_table.find_all('tr')
        team1 = rows[0].find('a')['href']
        team1_abbr = team1.split('/')[2]
        score1 = rows[0].find_all('td')[1].text
        team2 = rows[1].find('a')['href']
        team2_abbr = team2.split('/')[2]
        score2 = rows[1].find_all('td')[1].text
        box_score_path = game.find('p', class_='links').find('a')['href']
        box_score_link = f"{basketball_reference_url}{box_score_path}"

        games_data.append({
            'teams': f"{team1_abbr} vs {team2_abbr}",
            'score': f"{score1}-{score2}", 
            'box_score_link': box_score_link, 
            # 'players-played': get_players_played(box_score_link, team1_abbr) + get_players_played(box_score_link, team2_abbr)
        })
        all_teams_played.update([team1_abbr, team2_abbr])

    return games_data, all_teams_played

def get_players_played(box_score_link, team_abbrev):
    response = requests.get(box_score_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    table_id = f"box-{team_abbrev}-game-basic"
    table = soup.find('table', id=table_id)
    player_ids = []
    if table:
        rows = table.find_all('tr', class_=lambda x: x not in ['thead', 'over_header', 'rowSum'])
        for row in rows:
            player_link = row.find('a', href=lambda x: x and '/players/' in x)
            if not player_link:
                continue
            mp_cell = row.find('td', {'data-stat': 'mp'})
            if mp_cell and mp_cell.text.strip() and mp_cell.text != '0:00':
                player_href = player_link['href']
                player_id = player_href.split('/')[-1].replace('.html', '')
                player_ids.append(player_id)
    
    return player_ids

print(scrape_today_games(30, 3, 2025))
# print(scrape_today_games())
