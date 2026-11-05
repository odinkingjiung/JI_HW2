import threading
import time
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
CACHE_TTL_SECONDS = 60
_cache = {}
_cache_lock = threading.Lock()
_metrics_lock = threading.Lock()
metrics = {"http_requests": 0, "http_failures": 0, "steam_requests": 0, "steam_successes": 0, "steam_failures": 0, "steam_cache_hits": 0, "steam_cache_misses": 0, "steam_total_latency_ms": 0.0}


class SteamAPIError(Exception):
    pass


def get_players(game):
    appid = game["appid"]
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(appid)
        if cached and now - cached["stored_at"] < CACHE_TTL_SECONDS:
            with _metrics_lock:
                metrics["steam_cache_hits"] += 1
            return cached["players"]
        with _metrics_lock:
            metrics["steam_cache_misses"] += 1
            metrics["steam_requests"] += 1
    started = time.perf_counter()
    try:
        response = requests.get(STEAM_URL, params={"appid": appid}, timeout=8)
        response.raise_for_status()
        players = response.json().get("response", {}).get("player_count")
        if not isinstance(players, int):
            raise SteamAPIError("Steam returned an invalid player count.")
        with _cache_lock:
            _cache[appid] = {"players": players, "stored_at": time.monotonic()}
        with _metrics_lock:
            metrics["steam_successes"] += 1
        return players
    except (requests.RequestException, ValueError) as exc:
        with _metrics_lock:
            metrics["steam_failures"] += 1
        raise SteamAPIError("Steam API is unavailable. Please try again later.") from exc
    finally:
        with _metrics_lock:
            metrics["steam_total_latency_ms"] += (time.perf_counter() - started) * 1000


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    with _metrics_lock:
        metrics["http_requests"] += 1
        if response.status_code >= 500:
            metrics["http_failures"] += 1
    response.headers["X-Response-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.2f}"
    return response


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"games": GAMES})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "steam-live-players"}


@app.get("/metrics")
async def metrics_endpoint():
    with _metrics_lock:
        result = dict(metrics)
    steam_count = result["steam_successes"] + result["steam_failures"]
    result["steam_average_latency_ms"] = round(result["steam_total_latency_ms"] / steam_count, 2) if steam_count else 0
    return result


@app.get("/api/players")
async def players(games: str | None = None):
    keys = games.split(",") if games else list(GAMES)
    unknown = [key for key in keys if key not in GAMES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown game information: {', '.join(unknown)}")
    try:
        result = [{"key": key, "name": GAMES[key]["name"], "players": get_players(GAMES[key])} for key in keys]
    except SteamAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"updated_at": datetime.now(timezone.utc).isoformat(), "games": result}


@app.get("/api/custom-player")
async def custom_player(appid: int, name: str):
    if appid <= 0 or not name.strip():
        raise HTTPException(status_code=400, detail="Enter a valid Steam App ID and game name.")
    try:
        players = get_players({"appid": appid})
    except SteamAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"key": f"custom-{appid}", "name": name.strip(), "players": players}


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
