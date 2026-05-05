import os
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعت لينك الفيديو وأنا هحملهولك 🔥")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_links[update.message.chat_id] = url

    keyboard = [
        [InlineKeyboardButton("🎥 فيديو", callback_data="video")],
        [InlineKeyboardButton("🎧 صوت", callback_data="audio")]
    ]

    await update.message.reply_text(
        "اختار نوع التحميل:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data["type"] = choice

    if choice == "audio":
        await query.edit_message_text("جاري تحميل الصوت...")
        await download_and_send(query, context, "bestaudio")
    else:
        keyboard = [
            [InlineKeyboardButton("360p", callback_data="360")],
            [InlineKeyboardButton("720p", callback_data="720")],
            [InlineKeyboardButton("1080p", callback_data="1080")]
        ]

        await query.edit_message_text(
            "اختار الجودة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def choose_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data
    await query.edit_message_text("جاري التحميل...")
    await download_and_send(query, context, f"best[height<={quality}]")

async def download_and_send(query, context, format_code):
    chat_id = query.message.chat_id
    url = user_links.get(chat_id)

    ydl_opts = {
        'format': format_code,
        'outtmpl': 'file.%(ext)s'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if context.user_data.get("type") == "audio":
            await context.bot.send_audio(chat_id, audio=open(filename, 'rb'))
        else:
            await context.bot.send_video(chat_id, video=open(filename, 'rb'))

        os.remove(filename)

    except:
        await context.bot.send_message(chat_id, "حصل خطأ")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(choose_type, pattern="^(video|audio)$"))
app.add_handler(CallbackQueryHandler(choose_quality, pattern="^(360|720|1080)$"))

app.run_polling()
