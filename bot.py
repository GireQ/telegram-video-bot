import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Получаем токен из переменной окружения (без .env)
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HF_API_URL = "https://video-analyzer-bot.hf.space/analyze"

async def analyze_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗️Пример: /analyze https://youtube.com/... ")
        return

    video_url = context.args[0]
    await update.message.reply_text(f"🎬 Анализирую видео...\n{video_url}")

    try:
        response = requests.post(HF_API_URL, data={"url": video_url})

        # Проверка на успешный ответ
        if response.status_code != 200:
            await update.message.reply_text("⚠️ Hugging Face API вернул ошибку.")
            return

        # Пробуем разобрать JSON
        try:
            result = response.json()
        except Exception:
            await update.message.reply_text("❌ Не удалось обработать ответ от Hugging Face (не JSON).")
            return

        # Форматируем ответ
        caption = f"📌 *{result.get('title', 'Видео')}*\n\n"
        caption += f"🧠 *Описание:* {result.get('description', 'Нет описания')}\n\n"
        transcript = result.get('transcript', '')
        if transcript:
            caption += f"🎙️ *Речь:* {transcript[:400]}...\n\n"
        visual = result.get('visual_summary', '')
        if visual:
            caption += f"🖼️ *Визуальный обзор:* {visual[:400]}..."

        # Отправляем сообщение с превью
        await update.message.reply_photo(
            photo=result.get("thumbnail"),
            caption=caption,
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка:\n{e}")

# Запуск приложения
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("analyze", analyze_video))
    print("🤖 Бот работает")
    app.run_polling()
