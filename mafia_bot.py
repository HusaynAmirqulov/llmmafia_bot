from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi!")

players = {}
roles = {}
game_started = False
night = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Mafia botiga xush kelibsan!\n"
        "/newgame — yangi o‘yin\n"
        "/join — o‘yinga qo‘shilish\n"
        "/startgame — o‘yinni boshlash\n"
        "/myrole — rolingni bilish"
    )

async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global players, roles, game_started
    players = {}
    roles = {}
    game_started = False
    await update.message.reply_text("🃏 Yangi Mafia o‘yini yaratildi!\n/join — qo‘shilish")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if game_started:
        return
    user = update.effective_user
    players[user.id] = user.first_name
    await update.message.reply_text(f"🧍 {user.first_name} o‘yinga qo‘shildi!")

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_started, night
    if len(players) < 4:
        await update.message.reply_text("❗ Kamida 4 o‘yinchi kerak!")
        return

    game_started = True
    night = True
    assign_roles()
    await update.message.reply_text("🌙 Kecha boshlandi...\nMafia uyg‘ondi!")

def assign_roles():
    ids = list(players.keys())
    random.shuffle(ids)
    roles[ids[0]] = "🕵️ Mafia"
    roles[ids[1]] = "🧑‍⚕️ Doctor"
    roles[ids[2]] = "👮 Sheriff"
    for i in ids[3:]:
        roles[i] = "🙂 Civil"

async def myrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = roles.get(user_id)
    if role:
        await update.message.reply_text(f"🎭 Sening roling: {role}")
    else:
        await update.message.reply_text("❌ Sen hali o‘yinga qo‘shilmagansan.")

print("🤖 Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newgame", newgame))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("myrole", myrole))

app.run_polling()
