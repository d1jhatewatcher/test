import os
import requests

# Set these as GitHub secrets
RIOT_API_KEY = os.environ["RIOT_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
RIOT_ID= os.environ["RIOT_ID"]
NAME = os.environ["NAME"]

PREV_FILE = "prev.txt"

def get_puuid():
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{RIOT_ID}?api_key={RIOT_API_KEY}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["puuid"]

def get_recent_matches(puuid, count=1):
    url = f"https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={RIOT_API_KEY}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_match_placement(puuid, match_id):
    url = f"https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    match_data = r.json()
    
    for participant in match_data["info"]["participants"]:
        if participant["puuid"] == puuid:
            return participant["placement"], participant["time_eliminated"]
    
    return None

def get_rank(puuid):
    url = f"https://na1.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={RIOT_API_KEY}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r = r.json()[0]
    rank_str = f"{r["tier"]} {r["rank"]} {r["leaguePoints"]} LP"
    return rank_str

def get_last_match_id():
    if os.path.exists(PREV_FILE):
        with open(PREV_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_match_id(match_id):
    with open(PREV_FILE, "w") as f:
        f.write(match_id)

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def placement_to_string(placement):
    if placement == 1:
        return "1st (SO LUCKY!!)"
    elif placement == 2:
        return "2nd"
    elif placement == 3:
        return "3rd"
    elif placement == 4:
        return "4th"
    else:
        return f"{placement}th (LMAO!!!)"

def main():
    try:
        puuid = get_puuid()
        matches = get_recent_matches(puuid, count=1)
        placement, game_length = get_match_placement(puuid, matches[0])
        game_length = int(game_length/60)
        rank = get_rank(puuid)
        if not matches:
            return

        latest = matches[0]
        prev = get_last_match_id()

        if latest != prev:
            placement_str = placement_to_string(placement)
            send_to_discord(f"{NAME} placed {placement_str} in a {game_length} minute game! Rank: {rank}!!")
            save_last_match_id(latest)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
