from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

GAMES = {
    "cs2": {"name": "Counter-Strike 2", "appid": 730},
    "pubg": {"name": "PUBG: BATTLEGROUNDS", "appid": 578080},
    "dota2": {"name": "Dota 2", "appid": 570},
}
STEAM_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"


class SteamAPIError(Exception):
    pass


def get_players(game):
    try:
        response = requests.get(STEAM_URL, params={"appid": game["appid"]}, timeout=8)
        response.raise_for_status()
        data = response.json()
        players = data.get("response", {}).get("player_count")
        if not isinstance(players, int):
            raise SteamAPIError("Steam이 유효한 접속자 수를 반환하지 않았습니다.")
        return players
    except (requests.RequestException, ValueError) as exc:
        raise SteamAPIError("Steam API에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.") from exc


@app.get("/")
def index():
    return render_template("index.html", games=GAMES)


@app.get("/api/players")
def players():
    requested = request.args.get("games")
    keys = requested.split(",") if requested else list(GAMES)
    unknown = [key for key in keys if key not in GAMES]
    if unknown:
        return jsonify({"error": f"알 수 없는 게임 정보입니다: {', '.join(unknown)}"}), 400
    result = []
    try:
        for key in keys:
            game = GAMES[key]
            result.append({"key": key, "name": game["name"], "players": get_players(game)})
    except SteamAPIError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"updated_at": datetime.now(timezone.utc).isoformat(), "games": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
