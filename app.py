from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Steam Live Players")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"games": GAMES})


@app.get("/api/players")
async def players(games: str | None = None):
    keys = games.split(",") if games else list(GAMES)
    unknown = [key for key in keys if key not in GAMES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"알 수 없는 게임 정보입니다: {', '.join(unknown)}")
    result = []
    try:
        for key in keys:
            game = GAMES[key]
            result.append({"key": key, "name": game["name"], "players": get_players(game)})
    except SteamAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"updated_at": datetime.now(timezone.utc).isoformat(), "games": result}


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
