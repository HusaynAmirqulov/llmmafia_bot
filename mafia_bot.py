from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot_ready_chats = set()
game_participants = {}      # chat_id : {user_id: name}
last_game_message = {}      # chat_id : message_id

# ===== MENYULAR =====
def group_ready_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tayyor :)", callback_data="ready")]
    ])

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        # Shaxsiy chat uchun menyu
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌚 O'yinni guruhingizga qo'shing", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("💎 Premium guruhlar", callback_data="premium")],
            [InlineKeyboardButton("🔈 Mafia o‘yini qoidalari", callback_data="rules")],
            [InlineKeyboardButton("🔜 Yangiliklar", url="https://t.me/LLMMafiaOfficial")]
        ])
        await update.message.reply_text(
            "Salom! 👋\nMen 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman.",
            reply_markup=keyboard
        )
    else:
        # Guruhda start
        text = (
            "Salom! 👋\n"
            "Men 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman.\n\n"
            "☑️ Xabarlarni o‘chirish\n"
            "☑️ O‘yinchilarni bloklash\n"
            "☑️ Xabarlarni pin qilish"
        )
        await update.message.reply_text(
            text,
            reply_markup=group_ready_menu()
        )

# ===== BOT HUQUQLARI =====
async def check_bot_permissions(chat_id, context):
    bot = await context.bot.get_me()
    member = await context.bot.get_chat_member(chat_id, bot.id)
    return (
        member.status == "administrator" and
        member.can_delete_messages and
        member.can_restrict_members and
        member.can_pin_messages
    )

# ===== TUGMALAR =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    # Tayyor tugmasi
    if query.data == "ready":
        if not await check_bot_permissions(chat_id, context):
            await query.message.reply_text(
                "❌ Bot hali to‘liq admin emas!\n\n"
                "Iltimos, botga quyidagi huquqlarni bering:\n"
                "☑️ Xabarlarni o‘chirish\n"
                "☑️ O‘yinchilarni bloklash\n"
                "☑️ Xabarlarni pin qilish"
            )
            return
        bot_ready_chats.add(chat_id)
        await query.message.reply_text(
            "✅ Bot guruhda ishlashga tayyor!\n"
            "O‘yinni boshlash uchun /newgame buyrug‘idan foydalaning."
        )

    # Qoidalar
    elif query.data == "rules":
        await query.message.edit_text(
            "🔈 Mafia o‘yini qoidalari:\n\n"
            "1️⃣ O‘yinchilar rollarga bo‘linadi\n"
            "2️⃣ Mafia yashirincha harakat qiladi\n"
            "3️⃣ Kun davomida ovoz beriladi\n"
            "4️⃣ Mafia yoki Civil g‘alaba qozonadi",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]])
        )

    # Premium
    elif query.data == "premium":
        await query.message.edit_text(
            "💎 Premium imkoniyatlar:\n\n"
            "• Ko‘proq rollar\n"
            "• Tezkor o‘yin\n"
            "• Reklamasiz\n\n"
            "Tez orada 🚀",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]])
        )

    elif query.data == "back":
        await query.message.edit_text(
            "Salom! 👋\nMen 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman.",
            reply_markup=group_ready_menu()
        )

# ===== /newgame =====
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Eski buyruqni o'chirish
    try:
        await update.message.delete()
    except:
        pass

    # Bot adminligini tekshiramiz
    if not await check_bot_permissions(chat_id, context):
        await update.message.reply_text(
            "❌ Bot hali to‘liq admin emas!\n"
            "Iltimos, botga quyidagi huquqlarni bering:\n"
            "☑️ Xabarlarni o‘chirish\n"
            "☑️ O‘yinchilarni bloklash\n"
            "☑️ Xabarlarni pin qilish"
        )
        return

    bot_ready_chats.add(chat_id)

    # Guruhdagi o‘yinchilarni tekshirish
    if chat_id not in game_participants:
        game_participants[chat_id] = {}

    # Eski pinni ochish
    if chat_id in last_game_message:
        try:
            await context.bot.unpin_chat_message(chat_id)
        except:
            pass

    # Join link
    join_link = f"https://t.me/{context.bot.username}?start=game_{chat_id}"

    # O‘yinni boshlash xabari
    msg = await update.message.reply_text(
        "Ro'yxatdan o'tish boshlandi ⚡️\n\nJami 0 ta odam.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Qo‘shilish 🤵🏻", url=join_link)]
        ])
    )

    # Pin qilamiz
    await context.bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
    last_game_message[chat_id] = msg.message_id


    # join link
    join_link = f"https://t.me/{context.bot.username}?start=game_{chat_id}"

    msg = await update.message.reply_text(
        "Ro'yxatdan o'tish boshlandi ⚡️\n\nJami 0 ta odam.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Qo‘shilish 🤵🏻", url=join_link)]
        ])
    )

    await context.bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
    last_game_message[chat_id] = msg.message_id

# ===== /leave =====
async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in game_participants or user.id not in game_participants[chat_id]:
        await update.message.reply_text("❗ Siz allaqachon o‘yinda emassiz")
        return

    del game_participants[chat_id][user.id]

    names = ", ".join(game_participants[chat_id].values())
    total = len(game_participants[chat_id])

    if chat_id in last_game_message:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=last_game_message[chat_id],
                text=(
                    "Ro'yxatdan o'tish boshlandi ⚡️\n\n"
                    f"{names}\n\n"
                    f"Jami {total} ta odam."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "Qo‘shilish 🤵🏻",
                        url=f"https://t.me/{context.bot.username}?start=game_{chat_id}"
                    )]
                ])
            )
        except:
            pass

    await update.message.delete()


print("🤖 LunarLegacy Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newgame", newgame))
app.add_handler(CommandHandler("leave", leave))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
