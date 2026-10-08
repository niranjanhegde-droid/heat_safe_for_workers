import os
import sqlite3

PATH = os.getenv("DB_PATH", "heatsafe.db")


def conn():
    c = sqlite3.connect(PATH)
    c.row_factory = sqlite3.Row
    return c


def q(sql, *args):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def run(sql, *args):
    with conn() as c:
        c.execute(sql, args)


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(chat_id INTEGER PRIMARY KEY, lang TEXT, job TEXT, lat REAL, lon REAL,
            last_level INTEGER DEFAULT 0, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, chat_id INTEGER, lat REAL, lon REAL,
            felt TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY, chat_id INTEGER, level INTEGER, kind TEXT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS calibration(id INTEGER PRIMARY KEY, lat REAL, lon REAL, meter REAL,
            model REAL, ts TEXT DEFAULT CURRENT_TIMESTAMP);""")
        for col in ("acc INTEGER DEFAULT 0", "risk INTEGER DEFAULT 0", "joined TEXT"):  # migrate v1 databases
            try:
                c.execute(f"ALTER TABLE users ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass


def save_user(chat_id, lang, job, lat, lon, acc, risk):
    run("""INSERT INTO users(chat_id,lang,job,lat,lon,acc,risk,joined,active) VALUES(?,?,?,?,?,?,?,datetime('now'),1)
        ON CONFLICT(chat_id) DO UPDATE SET lang=?,job=?,lat=?,lon=?,acc=?,risk=?,active=1""",
        chat_id, lang, job, lat, lon, acc, risk, lang, job, lat, lon, acc, risk)


def get_user(chat_id):
    r = q("SELECT * FROM users WHERE chat_id=? AND active=1", chat_id)
    return r[0] if r else None


def active_users(job=None):
    return q("SELECT * FROM users WHERE active=1" + (" AND job=?" if job else ""), *([job] if job else []))


def set_level(chat_id, level):
    run("UPDATE users SET last_level=? WHERE chat_id=?", level, chat_id)


def deactivate(chat_id):
    run("UPDATE users SET active=0 WHERE chat_id=?", chat_id)


def log_alert(chat_id, level, kind):
    run("INSERT INTO alerts(chat_id,level,kind) VALUES(?,?,?)", chat_id, level, kind)


def add_feedback(chat_id, felt, lat, lon):
    run("INSERT INTO feedback(chat_id,lat,lon,felt) VALUES(?,?,?,?)", chat_id, lat, lon, felt)


def add_calibration(lat, lon, meter, model):
    run("INSERT INTO calibration(lat,lon,meter,model) VALUES(?,?,?,?)", lat, lon, meter, model)


def bias() -> float:
    """Mean (meter - model) over the last 30 readings, clamped to ±3°C."""
    v = q("SELECT AVG(meter-model) b FROM (SELECT * FROM calibration ORDER BY id DESC LIMIT 30)")[0]["b"]
    return round(max(-3.0, min(3.0, v or 0.0)), 2)


def stats():
    by_job = q("SELECT job, COUNT(*) n FROM users WHERE active=1 GROUP BY job")
    return {"workers": sum(r["n"] for r in by_job), "by_job": {r["job"]: r["n"] for r in by_job}}
