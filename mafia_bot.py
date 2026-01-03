from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot_ready_chats = set()  # qaysi guruhlar tayyor

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type

    # 🔹 SHAXSIY CHAT
    if chat_type == "private":
        text = (
            "Salom! 👋\n"
            "Men 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman."
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "O'yinni guruhingizga qo'shing 🌚",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("Premium guruhlar 💎", callback_data="premium"),
                InlineKeyboardButton(
                    "Yangiliklar 🔜",
                    url="https://t.me/LLMMafiaOfficial"
                )
            ],
            [
                InlineKeyboardButton("O'yin qoidalari 🔈", callback_data="rules")
            ]
        ]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 🔹 GURUH / SUPERGROUP
    else:
        text = (
            "Salom! 👋\n"
            "Men 𝐋𝐮𝐧𝐚𝐫𝐋𝐞𝐠𝐚𝐜𝐲 𝐌𝐚𝐟𝐢𝐚 guruhining 🤵🏻 Mafia o'yini botiman.\n\n"
            "☑️ Xabarlarni o‘chirish\n"
            "☑️ O‘yinchilarni bloklash\n"
            "☑️ Xabarlarni pin qilish"
        )

        keyboard = [
            [InlineKeyboardButton("Tayyor :)", callback_data="ready")]
        ]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Bot huquqlarini tekshirish
async def check_bot_permissions(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot = await context.bot.get_me()
    member = await context.bot.get_chat_member(chat_id, bot.id)

    # Faqat admin bo'lsa tekshiramiz
    if member.status != "administrator":
        return False

    # Zarur huquqlarni tekshirish
    return (
        getattr(member, "can_delete_messages", False) and
        getattr(member, "can_restrict_members", False) and
        getattr(member, "can_pin_messages", False)
    )

# Tugmalar bosilganda ishlaydi
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "premium":
        await query.message.reply_text(
            "💎 Premium guruhlar:\n\n"
            "• Ko‘proq rollar\n"
            "• Tezkor o‘yin\n"
            "• Reklamasiz\n\n"
            "Tez orada! 🚀"
        )

    elif query.data == "rules":
        await query.message.reply_text(
            "🔈 Mafia o‘yini qoidalari:\n\n"
            "1️⃣ O‘yinchilar rollarga bo‘linadi\n"
            "2️⃣ Mafia yashirincha harakat qiladi\n"
            "3️⃣ Kun davomida ovoz beriladi\n"
            "4️⃣ Mafia yoki Civil g‘alaba qozonadi"
        )

    elif query.data == "ready":
        chat_id = query.message.chat.id

        has_rights = await check_bot_permissions(chat_id, context)

        if not has_rights:
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
            "✅ Bot barcha huquqlarga ega!\n"
            "🎮 Endi o‘yinni boshlash mumkin.\n\n"
            "👉 /newgame"
        )

# Yangi o‘yin boshlash
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in bot_ready_chats:
        await update.message.reply_text(
            "⛔ Bot hali tayyor emas!\n"
            "Admin botga barcha huquqlarni berib, "
            "`Tayyor :)` tugmasini bosishi kerak."
        )
        return

    await update.message.reply_text("🎲 Yangi o‘yin boshlandi! Rollar tayyorlanmoqda...")

print("🤖 LunarLegacy Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newgame", newgame))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
