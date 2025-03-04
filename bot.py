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

user_client = TelegramClient(StringSession(), api_id, api_hash)  # Foydalanuvchi sessiyasi
bot = TelegramClient('bot_session', api_id, api_hash)  # Bot sessiyasi

last_code = "Hali kod olinmadi."
subscribers = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Salom! Kodni kiriting:")
    subscribers[event.sender_id] = {'valid': False, 'blocked': False}

@bot.on(events.NewMessage(pattern='/block'))
async def block(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = True
        await event.respond("Siz bloklandiz!")
    else:
        await event.respond("Avval /start buyrug‘ini yuboring.")

@bot.on(events.NewMessage)
async def receive_code(event):
    if event.sender_id in subscribers and event.text == "0066":
        subscribers[event.sender_id]['valid'] = True
        await event.respond("Kod to‘g‘ri! Endi 777000'dan kelgan yangi kodni kuting...")
        await event.delete()  # Xabarni o‘chirish

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
    await asyncio.gather(user_client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 8080})
    thread.start()
    asyncio.run(main())
