# Yangi global o'zgaruvchi ro'yxat uchun
game_registrations = {}  # chat_id: set(user_id)

# /newgame komandasi
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in bot_ready_chats:
        await update.message.reply_text(
            "⛔ Bot hali tayyor emas!\n"
            "Admin botga barcha huquqlarni berib, "
            "`Tayyor :)` tugmasini bosishi kerak."
        )
        return

    # Guruhda ro'yxatdan o'tish boshlanishi
    game_registrations[chat_id] = set()  # yangi o'yin uchun tozalash

    keyboard = [
        [InlineKeyboardButton("Qo'shilish 🤵🏻", callback_data="join_game")]
    ]
    text = "🎲 Yangi o‘yin boshlandi!\n\n⚡️ Ro'yxatdan o'tish boshlandi ⚡️\n\nJami 0 odam."
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Tugmalar handlerini yangilaymiz
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    user = query.from_user

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

    # Ro'yxatdan qo'shish tugmasi
    elif query.data == "join_game":
        if chat_id not in game_registrations:
            # O'yin boshlanmagan
            await query.message.reply_text("⚠️ O'yin hali boshlanmagan!")
            return

        if user.id in game_registrations[chat_id]:
            await user.send_message("Siz allaqachon ro'yxatga qo‘shilgansiz!")
            return

        game_registrations[chat_id].add(user.id)

        # Ro'yxatni yangilash matni
        users_nicknames = []
        for uid in game_registrations[chat_id]:
            member = await context.bot.get_chat_member(chat_id, uid)
            users_nicknames.append(f"• {member.user.first_name}")

        text = (
            "⚡️ Ro'yxatdan o'tish boshlandi ⚡️\n\n" +
            "\n".join(users_nicknames) +
            f"\n\nJami {len(users_nicknames)} odam."
        )

        # Xabarni yangilash (edit qilamiz)
        await query.message.edit_text(text, reply_markup=query.message.reply_markup)

        # Foydalanuvchiga shaxsiy xabar
        await user.send_message("Siz o‘yinga omadli qo‘shildingiz 😊")
