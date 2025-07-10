import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_URL = "https://video-analyzer-bot.hf.space/analyze"

async def analyze_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗️Пришли ссылку так: /analyze <YouTube URL>")
        return

    video_url = context.args[0]
    await update.message.reply_text(f"🎬 Анализирую: {video_url}...")

    try:
        response = requests.post(HF_API_URL, data={"url": video_url})
        result = response.json()

        caption = f"📌 *{result.get('title', 'Видео')}*\n\n"
        caption += f"🧠 *Описание:* {result.get('description', 'Нет')}\n\n"
        caption += f"🎙️ *Речь:* {result.get('transcript', '')[:400]}...\n\n"
        caption += f"🖼️ *Визуальный обзор:* {result.get('visual_summary', '')[:400]}..."

        await update.message.reply_photo(
            photo=result.get("thumbnail"),
            caption=caption,
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при анализе:\n{e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("analyze", analyze_video))
    print("🤖 Бот запущен")
    app.run_polling()
