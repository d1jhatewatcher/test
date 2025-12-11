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

def get_match_data(match_id):
    url = f"https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def extract_player_data(match_json, puuid):
    for p in match_json["info"]["participants"]:
        if p["puuid"] == puuid:
            return p
    return None

def get_rank(puuid):
    url = f"https://na1.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={RIOT_API_KEY}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r = r.json()[0]
    return f"{r['tier'].title()} {r['rank']} {r['leaguePoints']} LP"

def get_last_match_id():
    if os.path.exists(PREV_FILE):
        with open(PREV_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_match_id(match_id):
    with open(PREV_FILE, "w") as f:
        f.write(match_id)

def send_to_discord(message, gif_url):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message, "embeds": [{"image": {"url": gif_url}}]})

def placement_to_string(p):
    if p == 1:
        return "1st"
    elif p == 2:
        return "2nd"
    elif p == 3:
        return "3rd"
    else:
        return f"{p}th"

def format_traits(traits):
    active = [t for t in traits if t["tier_current"] > 0]
    return ", ".join([f"{t['name'].replace('TFT16_', '')} {t['tier_current']}" for t in active])
    
def format_units(units):
    lines = []
    for u in units:
        stars = "★" * u["tier"] 
        name = u["character_id"].replace("TFT16_", "").replace("TFT9_", "").replace("TFT", "").replace("16_", "")
        lines.append(f"{stars} {name}")
    return ", ".join(lines)

def main():
    try:
        puuid = get_puuid()
        matches = get_recent_matches(puuid, count=1)
        if not matches:
            return
        
        latest = matches[0]
        prev = get_last_match_id()

        if latest == prev:
            return 

        match_json = get_match_data(latest)
        player = extract_player_data(match_json, puuid)

        placement = player["placement"]
        duration = int(player["time_eliminated"] / 60)
        rank = get_rank(puuid)

        traits = format_traits(player["traits"])
        units = format_units(player["units"])

        placement_str = placement_to_string(placement)

        gif_url = ""
        if placement_str == 8:
            gif_url = "https://tenor.com/view/lol-gif-11059538064120696238"
            
        msg = (
            f"{NAME} placed {placement_str}!\n"
            f"Rank: {rank}\n"
            f"Duration: {duration} mins\n"
            f"Units: {units}\n"
            f"Traits: {traits}"
        )

        send_to_discord(msg, gif_url)
        save_last_match_id(latest)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
