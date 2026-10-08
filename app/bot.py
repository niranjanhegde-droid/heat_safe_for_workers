import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

from telegram import (InlineKeyboardButton as B, InlineKeyboardMarkup as M, KeyboardButton,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from . import db, heat, messages as m, weather

IST = ZoneInfo("Asia/Kolkata")
log = logging.getLogger("heatsafe")


async def user_plan(u) -> dict:
    return heat.build_plan(await weather.fetch_hours(u["lat"], u["lon"]), u["job"],
                           heat.risk_shift(u["acc"], u["risk"]))


def fb_markup(lang):
    t = m.tr(lang)
    return M([[B(t["fb_hot"], callback_data="fb:hot"), B(t["fb_ok"], callback_data="fb:ok")]])


def yes_no(lang, key):
    t = m.tr(lang)
    return M([[B(t["yes"], callback_data=f"{key}:1"), B(t["no"], callback_data=f"{key}:0")]])


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[B(name, callback_data=f"lang:{code}")] for code, name in m.LANGS.items()]
    await update.message.reply_text("Choose your language / भाषा चुनें / ಭಾಷೆ ಆರಿಸಿ", reply_markup=M(kb))


async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kind, val = q.data.split(":")
    d = ctx.user_data
    lang = d.get("lang", "en")
    if kind == "lang":
        d["lang"] = val
        kb = [[B(n, callback_data=f"job:{k}")] for k, n in m.JOBS[val].items()]
        await q.message.reply_text(m.tr(val)["job_q"], reply_markup=M(kb))
    elif kind == "job":
        d["job"] = val
        await q.message.reply_text(m.tr(lang)["acc_q"], reply_markup=yes_no(lang, "acc"))
    elif kind == "acc":
        d["acc"] = int(val)
        await q.message.reply_text(m.tr(lang)["risk_q"], reply_markup=yes_no(lang, "risk"))
    elif kind == "risk":
        d["risk"] = int(val)
        t = m.tr(lang)
        kb = ReplyKeyboardMarkup([[KeyboardButton(t["loc_btn"], request_location=True)]],
                                 resize_keyboard=True, one_time_keyboard=True)
        await q.message.reply_text(t["loc_q"], reply_markup=kb)
    elif kind == "fb":
        u = db.get_user(q.message.chat_id)
        if u:
            db.add_feedback(u["chat_id"], val, u["lat"], u["lon"])
        await q.message.reply_text(m.tr(u["lang"] if u else "en")["fb_thx"])


async def on_location(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d, loc = ctx.user_data, update.message.location
    if not {"lang", "job", "acc", "risk"} <= d.keys():
        return await update.message.reply_text("Send /start first.")
    db.save_user(update.effective_chat.id, d["lang"], d["job"], loc.latitude, loc.longitude, d["acc"], d["risk"])
    t = m.tr(d["lang"])
    await update.message.reply_text(t["done"] + "\n\n" + t["disc"], reply_markup=ReplyKeyboardRemove())
    await plan_cmd(update, ctx)


async def plan_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = db.get_user(update.effective_chat.id)
    if not u:
        return await update.message.reply_text(m.tr("en")["nouser"])
    await update.message.reply_text(m.plan_text(u["lang"], await user_plan(u)), reply_markup=fb_markup(u["lang"]))


async def dizzy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = db.get_user(update.effective_chat.id)
    await update.message.reply_text(m.tr(u["lang"] if u else "en")["firstaid"])


async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = db.get_user(update.effective_chat.id)
    db.deactivate(update.effective_chat.id)
    await update.message.reply_text(m.tr(u["lang"] if u else "en")["stop"])


async def morning_plans(ctx: ContextTypes.DEFAULT_TYPE):
    for u in db.active_users():
        try:
            plan = await user_plan(u)
            await ctx.bot.send_message(u["chat_id"], m.plan_text(u["lang"], plan), reply_markup=fb_markup(u["lang"]))
            db.log_alert(u["chat_id"], plan["level"], "plan")
        except Exception as e:  # one bad user must not stop the loop
            log.warning("plan failed for %s: %s", u["chat_id"], e)


async def check_alerts(ctx: ContextTypes.DEFAULT_TYPE):
    """Alert only when current-hour risk rises to High or above (avoids alert fatigue)."""
    now_h = datetime.now(IST).hour
    for u in db.active_users():
        try:
            plan = await user_plan(u)
            lvl = heat.level_at(plan, now_h)
            if lvl >= 2 and lvl > u["last_level"]:
                plan = {**plan, "level": lvl, "work": heat.WORK_REST[lvl][0], "rest": heat.WORK_REST[lvl][1]}
                await ctx.bot.send_message(u["chat_id"], m.plan_text(u["lang"], plan, "alert"),
                                           reply_markup=fb_markup(u["lang"]))
                db.log_alert(u["chat_id"], lvl, "alert")
            db.set_level(u["chat_id"], lvl)
        except Exception as e:
            log.warning("alert failed for %s: %s", u["chat_id"], e)


def build(token: str) -> Application:
    app = Application.builder().token(token).build()
    for name, fn in (("start", start), ("plan", plan_cmd), ("dizzy", dizzy), ("stop", stop)):
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.LOCATION, on_location))
    app.job_queue.run_daily(morning_plans, time=time(7, 0, tzinfo=IST))
    app.job_queue.run_repeating(check_alerts, interval=1800, first=60)
    return app
