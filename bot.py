from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl import types
import asyncio
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlavoti"

api_id = 1150656  # To'g'ri API ID kiriting
api_hash = "fb33d7c76f5bdaab44d5145537de31c0"  # To'g'ri API hash kiriting
bot_token = "8108266498:AAHTewUwY8lXDlfklgvnzDC_4raqp2csdHc"  # Telegram bot tokenini kiriting

# Yangi sessiya yaratish
user_client = TelegramClient(StringSession(), api_id, api_hash)
bot = TelegramClient('bot_session', api_id, api_hash)

last_code = "Hali kod olinmadi."
subscribers = {}
user_sequences = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Karochi Admin bo'lsang kodni bilasan, Davay kod keremi yozasan 💪 :")
    subscribers[event.sender_id] = {'valid': False, 'blocked': False}
    user_sequences[event.sender_id] = []

@bot.on(events.NewMessage(pattern='/block'))
async def block(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = True
        await event.respond("Siz bloklandiz!")
    else:
        await event.respond("Avvalo, /start komandasini yuboring.")

@bot.on(events.NewMessage)
async def receive_code(event):
    if event.sender_id in subscribers:
        if event.text == "0066":
            subscribers[event.sender_id]['valid'] = True
            await event.respond("Kod muvaffaqiyatli kiritildi! Endi 777000'dan kelgan yangi kodni kuting...")

        if subscribers[event.sender_id]['valid'] and not subscribers[event.sender_id]['blocked']:
            await event.respond(f"Yangi Telegram kodi: {last_code}")
        elif subscribers[event.sender_id]['blocked']:
            await event.respond("Siz bloklandiz va kod yuborilmaydi.")

@user_client.on(events.NewMessage(from_users=777000))
async def new_code_handler(event):
    global last_code
    last_code = event.text
    for user_id, status in subscribers.items():
        if status['valid'] and not status['blocked']:
            await bot.send_message(user_id, f"Yangi Telegram kodi: {last_code}")

async def main():
    await user_client.start()
    print("User client ishga tushdi...")
    await bot.start(bot_token=bot_token)
    print("Bot ishga tushdi...")
    await asyncio.Event().wait()  # Kodni to'xtamasdan ushlab turish

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Dastur to'xtatildi.")
