import csv, io, os, secrets
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

load_dotenv()
from . import bot, db, heat, weather  # noqa: E402

STATIC = Path(__file__).parent / "static"
IST = ZoneInfo("Asia/Kolkata")
security = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    heat.set_offset(db.bias())
    app.state.tg = None
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:  # dashboard and admin still work without a token
        app.state.tg = bot.build(token)
        tg = app.state.tg
        await tg.initialize(); await tg.start(); await tg.updater.start_polling()
    yield
    if app.state.tg:
        tg = app.state.tg
        await tg.updater.stop(); await tg.stop(); await tg.shutdown()


app = FastAPI(title="HeatSafe", lifespan=lifespan)


def admin(c: HTTPBasicCredentials = Depends(security)):
    """HTTP Basic auth. Admin is disabled entirely until ADMIN_PASSWORD is set."""
    user, pw = os.getenv("ADMIN_USER", "admin"), os.getenv("ADMIN_PASSWORD")
    ok = bool(pw) and secrets.compare_digest(c.username, user) and secrets.compare_digest(c.password, pw)
    if not ok:
        raise HTTPException(401, "Unauthorized", headers={"WWW-Authenticate": "Basic"})


@app.get("/")
def dashboard():
    return FileResponse(STATIC / "dashboard.html")


@app.get("/api/risk")
async def risk(lat: float = Query(12.97), lon: float = Query(77.59), job: str = "delivery",
               new_to_heat: bool = False, high_risk: bool = False):
    plan = heat.build_plan(await weather.fetch_hours(lat, lon), job, heat.risk_shift(new_to_heat, high_risk))
    return {**plan, "level_name": heat.LEVELS[plan["level"]]}


@app.get("/api/stats")
def stats():
    return db.stats()


# ---------------- admin ----------------
@app.get("/admin", dependencies=[Depends(admin)])
def admin_page():
    return FileResponse(STATIC / "admin.html")


@app.get("/api/admin/overview", dependencies=[Depends(admin)])
async def overview():
    now_h, users, zones = datetime.now(IST).hour, [], {}
    for u in db.active_users():
        lvl = w = None
        try:
            plan = heat.build_plan(await weather.fetch_hours(u["lat"], u["lon"]), u["job"],
                                   heat.risk_shift(u["acc"], u["risk"]))
            lvl = heat.level_at(plan, now_h)
            w = next((r["wbgt"] for r in plan["rows"] if r["hour"] == now_h), None)
        except Exception:
            pass
        z = f'{round(u["lat"], 1)}, {round(u["lon"], 1)}'
        users.append({"id": "…" + str(u["chat_id"])[-4:], "job": u["job"], "lang": u["lang"], "zone": z,
                      "level": lvl, "wbgt": w, "new_to_heat": bool(u["acc"]), "high_risk": bool(u["risk"]),
                      "joined": u["joined"]})
        zz = zones.setdefault(z, {"zone": z, "n": 0, "max_level": 0})
        zz["n"] += 1
        zz["max_level"] = max(zz["max_level"], lvl or 0)
    fb = {r["felt"]: r["n"] for r in db.q("SELECT felt, COUNT(*) n FROM feedback GROUP BY felt")}
    tot = sum(fb.values())
    return {
        "kpi": {"workers": len(users), "alerts_24h": db.q("SELECT COUNT(*) n FROM alerts WHERE kind='alert' AND ts > datetime('now','-1 day')")[0]["n"],
                "too_hot_pct": round(100 * fb.get("hot", 0) / tot) if tot else None, "feedback": tot, "bias": db.bias()},
        "by_job": db.q("SELECT job k, COUNT(*) n FROM users WHERE active=1 GROUP BY job"),
        "by_lang": db.q("SELECT lang k, COUNT(*) n FROM users WHERE active=1 GROUP BY lang"),
        "users": users, "zones": sorted(zones.values(), key=lambda z: -z["max_level"]),
        "alerts": db.q("SELECT level, kind, ts FROM alerts ORDER BY id DESC LIMIT 15"),
        "feedback": db.q("SELECT felt, lat, lon, ts FROM feedback ORDER BY id DESC LIMIT 15"),
        "calibration": db.q("SELECT meter, model, ts FROM calibration ORDER BY id DESC LIMIT 10"),
    }


class Broadcast(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    job: str | None = None


@app.post("/api/admin/broadcast", dependencies=[Depends(admin)])
async def broadcast(b: Broadcast):
    tg = app.state.tg
    if not tg:
        raise HTTPException(503, "Telegram bot is not running. Set TELEGRAM_BOT_TOKEN.")
    sent = 0
    for u in db.active_users(b.job or None):
        try:
            await tg.bot.send_message(u["chat_id"], b.text)
            db.log_alert(u["chat_id"], 0, "broadcast")
            sent += 1
        except Exception:
            pass
    return {"sent": sent}


class Calib(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    meter_wbgt: float = Field(ge=5, le=50)


@app.post("/api/admin/calibrate", dependencies=[Depends(admin)])
async def calibrate(c: Calib):
    hours = await weather.fetch_hours(c.lat, c.lon)
    now = next((h for h in hours if int(h["time"][11:13]) == datetime.now(IST).hour), None)
    if not now:
        raise HTTPException(502, "No forecast for the current hour.")
    model = heat.wbgt(now["temp"], now["rh"], now["solar"], now.get("wind", 1.5), calibrated=False)
    db.add_calibration(c.lat, c.lon, c.meter_wbgt, round(model, 2))
    heat.set_offset(db.bias())
    return {"model_wbgt": round(model, 1), "new_bias": heat.OFFSET}


@app.get("/api/admin/feedback.csv", dependencies=[Depends(admin)])
def feedback_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["felt", "lat", "lon", "timestamp"])
    w.writerows([r["felt"], r["lat"], r["lon"], r["ts"]] for r in db.q("SELECT felt,lat,lon,ts FROM feedback ORDER BY id"))
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=feedback.csv"})
