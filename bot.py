import requests
import os

RIOT_API_KEY = os.environ["RIOT_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

PLAYER_PUUID = "REPLACE_WITH_PUUID"
REGION = "americas"

STATE_FILE = "last_match.txt"

def get_latest_match():
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{PLAYER_PUUID}/ids?start=0&count=1"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data[0] if data else None

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def read_last_match():
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

def write_last_match(match_id):
    with open(STATE_FILE, "w") as f:
        f.write(match_id)

def main():
    latest = get_latest_match()
    if not latest:
        return

    last = read_last_match()

    if latest != last:
        send_to_discord(f"🆕 New match detected: `{latest}`")
        write_last_match(latest)

if __name__ == "__main__":
    main()
