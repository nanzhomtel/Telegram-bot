import telebot
import yt_dlp
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Token ambil dari Railway Environment Variable
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ────────────────────────────────
# Fungsi downloader
# ────────────────────────────────
def download_video(url, is_audio=False):
    ydl_opts = {
        "format": "bestaudio/best" if is_audio else "bestvideo+bestaudio/best",
        "outtmpl": "%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4" if not is_audio else None,
    }
    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if is_audio:
            filename = os.path.splitext(filename)[0] + ".mp3"
        else:
            filename = os.path.splitext(filename)[0] + ".mp4"
    return filename

# ────────────────────────────────
# /start
# ────────────────────────────────
@bot.message_handler(commands=["start"])
def start(message):
    teks = (
        "👋 <b>Selamat datang di Downloader Bot!</b>\n\n"
        "📥 Kirim link TikTok / Instagram.\n"
        "Bot akan kasih pilihan format:\n"
        "🎵 MP3 atau 🎬 MP4 HD 🚀"
    )
    bot.reply_to(message, teks)

# ────────────────────────────────
# Handler link
# ────────────────────────────────
@bot.message_handler(func=lambda m: m.text.startswith("http"))
def handle_link(message):
    url = message.text.strip()
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}"),
        InlineKeyboardButton("🎬 MP4 HD", callback_data=f"mp4|{url}")
    )
    bot.reply_to(
        message,
        "🔗 Link diterima!\nPilih format yang ingin diunduh:",
        reply_markup=markup
    )

# ────────────────────────────────
# Callback
# ────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    action, url = call.data.split("|", 1)
    chat_id = call.message.chat.id

    if action == "mp3":
        wait_msg = bot.send_message(chat_id, "⏳ Sedang mengunduh audio MP3...")
        try:
            filename = download_video(url, is_audio=True)
            with open(filename, "rb") as f:
                bot.send_audio(chat_id, f)
            os.remove(filename)
            bot.delete_message(chat_id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Gagal unduh MP3: {e}", chat_id, wait_msg.message_id)

    elif action == "mp4":
        wait_msg = bot.send_message(chat_id, "⏳ Sedang mengunduh video HD...")
        try:
            filename = download_video(url, is_audio=False)
            with open(filename, "rb") as f:
                bot.send_video(chat_id, f, supports_streaming=True)
            os.remove(filename)
            bot.delete_message(chat_id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Gagal unduh MP4: {e}", chat_id, wait_msg.message_id)

print("🤖 Bot berjalan...")
bot.infinity_polling()
