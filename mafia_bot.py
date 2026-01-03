from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot_ready_chats = set()
game_participants = {}      # chat_id : {user_id: name}
last_game_message = {}      # chat_id : message_id


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].startswith("join_"):
        await update.message.reply_text(
            "✅ Siz o‘yinga omadli qo‘shildingiz 😊\n"
            "Endi guruhga qaytib o‘yinni davom ettiring."
        )
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "Salom! 👋\nMen LunarLegacy Mafia botiman 🤵🏻",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "O'yinni guruhga qo‘shish 🌚",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )]
            ])
        )
    else:
        await update.message.reply_text(
            "Botni admin qiling va tayyor tugmasini bosing 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Tayyor :)", callback_data="ready")]
            ])
        )


# Bot huquqlari
async def check_bot_permissions(chat_id, context):
    bot = await context.bot.get_me()
    member = await context.bot.get_chat_member(chat_id, bot.id)
    return (
        member.status == "administrator" and
        member.can_delete_messages and
        member.can_restrict_members and
        member.can_pin_messages
    )


# Tugmalar
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "ready":
        if not await check_bot_permissions(chat_id, context):
            await query.message.reply_text("❌ Botga to‘liq admin huquqlar bering!")
            return
        bot_ready_chats.add(chat_id)
        await query.message.reply_text("✅ Bot tayyor!\n👉 /newgame")

    elif query.data.startswith("join_game_"):
        user = query.from_user

        if chat_id not in game_participants:
            game_participants[chat_id] = {}

        if user.id in game_participants[chat_id]:
            await query.answer("❗ Siz allaqachon o‘yindasiz", show_alert=True)
            return

        name = f"{user.first_name} {user.last_name or ''}".strip()
        game_participants[chat_id][user.id] = name

        # DM tekshiramiz
        try:
            await context.bot.send_message(
                user.id, "Siz o‘yinga omadli qo‘shildingiz 😊"
            )
        except:
            start_link = f"https://t.me/{context.bot.username}?start=join_{chat_id}"
            await query.message.reply_text(
                "❗ O‘yinga to‘liq qo‘shilish uchun botni oching:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 Botni ochish", url=start_link)]
                ])
            )

        names = ", ".join(game_participants[chat_id].values())
        total = len(game_participants[chat_id])

        await query.message.edit_text(
            f"Ro'yxatdan o'tish boshlandi ⚡️\n\n"
            f"{names}\n\n"
            f"Jami {total} ta odam.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Qo‘shilish 🤵🏻", callback_data=f"join_game_{chat_id}")]
            ])
        )


# /newgame
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in bot_ready_chats:
        await update.message.reply_text("⛔ Bot hali tayyor emas!")
        return

    if chat_id not in game_participants:
        game_participants[chat_id] = {}

    # eski pinni ochamiz
    if chat_id in last_game_message:
        try:
            await context.bot.unpin_chat_message(chat_id)
        except:
            pass

    msg = await update.message.reply_text(
        "Ro'yxatdan o'tish boshlandi ⚡️\n\nJami 0 ta odam.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Qo‘shilish 🤵🏻", callback_data=f"join_game_{chat_id}")]
        ])
    )

    await context.bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
    last_game_message[chat_id] = msg.message_id


print("🤖 LunarLegacy Mafia bot ishga tushdi")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newgame", newgame))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
