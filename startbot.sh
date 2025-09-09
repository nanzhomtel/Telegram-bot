#!/data/data/com.termux/files/usr/bin/bash
cd ~/telebot
source venv/bin/activate

# Loop agar bot otomatis restart kalau crash
while true
do
  python bot.py
  echo "⚠️ Bot crash, restart dalam 5 detik..."
  sleep 5
done
