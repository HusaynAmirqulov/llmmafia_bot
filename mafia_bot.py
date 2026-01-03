from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

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
    await query.message.reply_text(
        "✅ Bot guruhda ishlashga tayyor!\n"
        "O‘yinni boshlash uchun /newgame buyrug‘idan foydalaning."
    )

print("🤖 LunarLegacy Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
