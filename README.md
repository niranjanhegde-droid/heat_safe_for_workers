# HeatSafe: heat-stress planner for outdoor workers

Telegram bot + FastAPI dashboard. Workers pick a language, job and location once, then get a
work/rest plan every morning (7 AM IST) and an alert when risk rises to High or Extreme.

**Stack:** Python 3.12, FastAPI, python-telegram-bot (job queue), Open-Meteo (free, no key),
SQLite, plain HTML/JS dashboard, Docker, pytest.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add TELEGRAM_BOT_TOKEN from @BotFather
pytest                      # heat engine tests
uvicorn app.main:app --reload
```
Open http://localhost:8000 for the dashboard and message your bot `/start` on Telegram.
Without a token the dashboard and API still run.
Docker: `docker build -t heatsafe . && docker run --env-file .env -p 8000:8000 heatsafe`

## How it works
`weather.py` (hourly temp/humidity/sun) -> `heat.py` (WBGT, workload risk, work/rest minutes)
-> `messages.py` (fixed EN/HI/KN templates) -> `bot.py` (delivery + scheduler).
Safety text is never LLM-generated.

## Before real use
1. Verify `THRESHOLDS` and `WORK_REST` in `heat.py` against ISO 7243 / ACGIH / NIOSH.
2. Have the Hindi and Kannada texts reviewed by native speakers.
3. Pilot with 10-20 workers; compare WBGT against a real meter if you can.

## Next steps
Personalization (acclimatization, age), voice notes (TTS), "felt too hot" feedback (table exists),
WhatsApp Cloud API, Postgres, employer dashboard, cool-spot map.

## v2: accuracy, personalization, admin panel
- **Model:** Stull wet-bulb + radiation/wind-aware WBGT (0.7 Tnwb + 0.2 Tg + 0.1 Ta).
- **Personal risk:** new-to-heat (+2 °C) and 45+/chronic condition (+1 °C) workers get stricter limits.
- **Field calibration:** enter real WBGT meter readings in the admin panel; the average error is corrected automatically.
- **Feedback:** "Too hot / Fine" buttons under plans and alerts; export as CSV.
- **Admin panel:** set `ADMIN_PASSWORD` in `.env`, open http://localhost:8000/admin. Shows workers, zones, live risk,
  alerts, feedback, calibration; sends broadcasts to all workers or one job type. Put it behind HTTPS before exposing it online.
- Existing v1 databases are migrated automatically on start.
