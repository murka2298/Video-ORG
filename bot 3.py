import os
import re
import logging
import tempfile
import subprocess

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import yt_dlp
import imageio_ffmpeg

# ------------------------------------------------------------------
# SOZLAMALAR
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # tokenni environment variable orqali beramiz
MAX_TELEGRAM_SIZE = 49 * 1024 * 1024  # ~50MB (Telegram bot API cheklovi)
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()  # tizimga o'rnatilgan ffmpeg shart emas

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(
    r"(https?://(?:www\.)?(?:instagram\.com|tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)\S+)"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n\n"
        "Menga Instagram yoki TikTok'dan video linkini yuboring.\n"
        "Men sizga:\n"
        "1) Original videoni (watermarksiz, mp4)\n"
        "2) Videoning boshqa formatdagi (mkv) nusxasini\n"
        "3) Videodagi musiqani alohida (mp3)\n"
        "qilib yuboraman."
    )


def download_video(url: str, out_dir: str) -> str:
    """yt-dlp yordamida videoni yuklab olib, fayl yo'lini qaytaradi."""
    outtmpl = os.path.join(out_dir, "source.%(ext)s")
    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "ffmpeg_location": FFMPEG_PATH,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        # merge_output_format tufayli kengaytma mp4 bo'lishi kerak
        base, _ = os.path.splitext(filepath)
        mp4_path = base + ".mp4"
        if os.path.exists(mp4_path):
            return mp4_path
        return filepath


def convert_video_format(src_path: str, out_dir: str, ext: str = "mkv") -> str:
    """Videoni boshqa konteyner formatiga o'giradi (qayta kodlashsiz, tez)."""
    dst_path = os.path.join(out_dir, f"video_converted.{ext}")
    cmd = [FFMPEG_PATH, "-y", "-i", src_path, "-c", "copy", dst_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst_path


def extract_audio(src_path: str, out_dir: str) -> str:
    """Videodan musiqani mp3 formatida ajratib oladi."""
    dst_path = os.path.join(out_dir, "audio.mp3")
    cmd = [
        FFMPEG_PATH, "-y", "-i", src_path,
        "-vn", "-acodec", "libmp3lame", "-q:a", "2",
        dst_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst_path


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = URL_PATTERN.search(text)
    if not match:
        await update.message.reply_text(
            "Iltimos, to'g'ri Instagram yoki TikTok linkini yuboring."
        )
        return

    url = match.group(1)
    status_msg = await update.message.reply_text("⏳ Video yuklanmoqda...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            video_path = download_video(url, tmp_dir)
        except Exception as e:
            logger.exception("Yuklab olishda xatolik")
            await status_msg.edit_text(f"❌ Videoni yuklab bo'lmadi: {e}")
            return

        try:
            converted_path = convert_video_format(video_path, tmp_dir, ext="mkv")
        except Exception:
            logger.exception("Formatni o'zgartirishda xatolik")
            converted_path = None

        try:
            audio_path = extract_audio(video_path, tmp_dir)
        except Exception:
            logger.exception("Audio ajratishda xatolik")
            audio_path = None

        await status_msg.edit_text("📤 Fayllar yuborilmoqda...")

        # Original video (mp4)
        if os.path.getsize(video_path) <= MAX_TELEGRAM_SIZE:
            with open(video_path, "rb") as f:
                await update.message.reply_video(f, caption="Original video (mp4)")
        else:
            await update.message.reply_text("⚠️ Original video 50MB dan katta, yuborib bo'lmadi.")

        # Konvertatsiya qilingan video (mkv)
        if converted_path and os.path.exists(converted_path):
            if os.path.getsize(converted_path) <= MAX_TELEGRAM_SIZE:
                with open(converted_path, "rb") as f:
                    await update.message.reply_document(f, caption="Boshqa formatdagi video (mkv)")
            else:
                await update.message.reply_text("⚠️ Konvertatsiya qilingan video 50MB dan katta.")

        # Musiqa (mp3)
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                await update.message.reply_audio(f, caption="Musiqa (mp3)")

        await status_msg.delete()


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Avval environment variable sifatida o'rnating."
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
