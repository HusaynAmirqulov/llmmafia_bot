from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot_ready_chats = set()   # qaysi guruhlar tayyor
game_players = {}         # {chat_id: [list of user full names]}
game_messages = {}        # {chat_id: message_id}  guruhdagi "Ro'yxatdan o'tish boshlandi ⚡️" xabar IDsi

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type

    if chat_type == "private":
        text = "Salom! 👋\nMen 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman."
        keyboard = [
            [InlineKeyboardButton("O'yinni guruhingizga qo'shing 🌚",
                                  url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("Premium guruhlar 💎", callback_data="premium"),
             InlineKeyboardButton("Yangiliklar 🔜", url="https://t.me/LLMMafiaOfficial")],
            [InlineKeyboardButton("O'yin qoidalari 🔈", callback_data="rules")]
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        text = (
            "Salom! 👋\n"
            "Men 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman.\n\n"
            "☑️ Xabarlarni o‘chirish\n"
            "☑️ O‘yinchilarni bloklash\n"
            "☑️ Xabarlarni pin qilish"
        )
        keyboard = [[InlineKeyboardButton("Tayyor :)", callback_data="ready")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Bot huquqlarini tekshirish
async def check_bot_permissions(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot = await context.bot.get_me()
    member = await context.bot.get_chat_member(chat_id, bot.id)
    if member.status != "administrator":
        return False
    return (
        getattr(member, "can_delete_messages", False) and
        getattr(member, "can_restrict_members", False) and
        getattr(member, "can_pin_messages", False)
    )

# Tugmalar bosilganda ishlaydi
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "premium":
        await query.message.reply_text(
            "💎 Premium guruhlar:\n• Ko‘proq rollar\n• Tezkor o‘yin\n• Reklamasiz\nTez orada! 🚀"
        )
    elif query.data == "rules":
        await query.message.reply_text(
            "🔈 Mafia o‘yini qoidalari:\n"
            "1️⃣ O‘yinchilar rollarga bo‘linadi\n"
            "2️⃣ Mafia yashirincha harakat qiladi\n"
            "3️⃣ Kun davomida ovoz beriladi\n"
            "4️⃣ Mafia yoki Civil g‘alaba qozonadi"
        )
    elif query.data == "ready":
        has_rights = await check_bot_permissions(chat_id, context)
        if not has_rights:
            await query.message.reply_text(
                "❌ Bot hali to‘liq admin emas!\nIltimos, botga barcha huquqlarni bering:\n"
                "☑️ Xabarlarni o‘chirish\n☑️ O‘yinchilarni bloklash\n☑️ Xabarlarni pin qilish"
            )
            return
        bot_ready_chats.add(chat_id)
        await query.message.reply_text(
            "✅ Bot barcha huquqlarga ega!\n🎮 Endi o‘yinni boshlash mumkin.\n\n👉 /newgame"
        )
    elif query.data == "join_game":
        user = query.from_user
        full_name = user.full_name
        players = game_players.get(chat_id, [])

        if full_name not in players:
            players.append(full_name)
        game_players[chat_id] = players

        # Guruhdagi "Ro'yxatdan o'tish boshlandi ⚡️" xabarini yangilash
        message_id = game_messages.get(chat_id)
        text = "Ro'yxatdan o'tish boshlandi ⚡️\n\n"
        for u in players:
            text += f"• {u}\n"
        text += f"\nJami {len(players)} odam."
        keyboard = [[InlineKeyboardButton("Qo'shilish 🤵🏻", callback_data="join_game")]]

        if message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass

        # Foydalanuvchiga DM
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text="Siz o‘yinga omadli qo‘shildingiz 😊",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Guruhga qaytish ⬅️", callback_data=f"back_to_group_{chat_id}")]]
                )
            )
        except:
            await query.message.reply_text(f"⚠️ {full_name}, siz botni start qilmagan, DM yuborolmadim.")

    elif query.data.startswith("back_to_group_"):
        # DMdagi tugma bosilganda foydalanuvchini guruh xabariga olib keladi
        gid = int(query.data.split("_")[-1])
        msg_id = game_messages.get(gid)
        if msg_id:
            await query.message.edit_text("⬆️ Guruhdagi ro‘yxatni ko‘ring.")
        else:
            await query.message.edit_text("⚠️ Guruh topilmadi.")

# Yangi o‘yin boshlash
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in bot_ready_chats:
        await update.message.reply_text(
            "⛔ Bot hali tayyor emas!\nAdmin botga barcha huquqlarni berib, `Tayyor :)` tugmasini bosishi kerak."
        )
        return

    game_players[chat_id] = []
    text = "Ro'yxatdan o'tish boshlandi ⚡️"
    keyboard = [[InlineKeyboardButton("Qo'shilish 🤵🏻", callback_data="join_game")]]
    msg = await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    game_messages[chat_id] = msg.message_id  # Guruhdagi xabar IDsi saqlanadi

print("🤖 LunarLegacy Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newgame", newgame))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
