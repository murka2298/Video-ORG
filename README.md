# Instagram/TikTok Downloader Telegram Bot

## Bot nima qiladi
Instagram yoki TikTok linkini yuborsangiz, bot sizga:
1. **Original videoni** (watermarksiz, `.mp4`)
2. **Videoning boshqa formatdagi nusxasini** (`.mkv`)
3. **Videodagi musiqani** alohida (`.mp3`)

qilib qaytaradi.

## 1-qadam: Telegram bot yaratish
1. Telegramda **@BotFather** ga yozing.
2. `/newbot` buyrug'ini yuboring.
3. Bot uchun nom va username bering (username `bot` bilan tugashi kerak, masalan `mening_video_botim_bot`).
4. BotFather sizga **token** beradi — uni saqlab qo'ying (masalan: `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxx`).

## 2-qadam: Kompyuterda tayyorlash
Sizga kerak bo'ladi:
- Python 3.10+
- **ffmpeg** (video/audio konvertatsiya uchun majburiy)

O'rnatish (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg python3-pip -y
```

macOS:
```bash
brew install ffmpeg
```

Windows: https://ffmpeg.org/download.html dan yuklab, PATH ga qo'shing.

## 3-qadam: Loyihani sozlash
```bash
pip install -r requirements.txt
```

Tokenni environment variable sifatida bering:

Linux/macOS:
```bash
export BOT_TOKEN="sizning_tokeningiz"
python3 bot.py
```

Windows (PowerShell):
```powershell
$env:BOT_TOKEN="sizning_tokeningiz"
python bot.py
```

Bot ishga tushgach, Telegramda o'sha botga `/start` yozing va Instagram yoki TikTok linkini yuboring.

## 4-qadam: Botni 24/7 ishlatish (doim onlayn turishi uchun)
O'z kompyuteringizni o'chirsangiz bot ham to'xtaydi. Doimiy ishlashi uchun quyidagilardan birini tanlang:
- **Railway.app** yoki **Render.com** — bepul/arzon, oson deploy qilinadi
- **VPS** (masalan, Timeweb, DigitalOcean) — `screen` yoki `systemd` orqali fon jarayoni sifatida ishga tushiring
- **PythonAnywhere**

Bularning barchasida qadamlar deyarli bir xil: repozitoriyni yuklaysiz, `BOT_TOKEN` ni environment variable sifatida kiritasiz, `pip install -r requirements.txt` va keyin `python bot.py` ni ishga tushirasiz (ffmpeg ham o'rnatilgan bo'lishi kerak).

## Eslatma
- Telegram bot orqali fayl yuborish chegarasi ~50MB. Undan katta videolar yuborilmaydi.
- Instagram ba'zan login talab qilishi mumkin (private akkauntlar yoki cheklangan kontent uchun) — bunday holatlarda yt-dlp cookie fayli talab qilishi mumkin.
