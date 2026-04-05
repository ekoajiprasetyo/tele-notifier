import os
import asyncio
import requests

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_CHAT_ID = int(os.environ["BOT_CHAT_ID"])

# Wajib untuk Heroku: session disimpan sebagai string di Config Vars
SESSION_STRING = os.environ["SESSION_STRING"]

WATCH_IDS = {
    int(x.strip())
    for x in os.environ.get("WATCH_IDS", "").split(",")
    if x.strip()
}

WATCH_USERNAMES = {
    x.strip().lower().replace("@", "")
    for x in os.environ.get("WATCH_USERNAMES", "").split(",")
    if x.strip()
}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


def send_bot_notification(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": BOT_CHAT_ID,
            "text": text
        },
        timeout=20
    )
    response.raise_for_status()


def is_watched(sender):
    if not sender:
        return False

    sender_id = getattr(sender, "id", None)
    username = getattr(sender, "username", None)

    if sender_id in WATCH_IDS:
        return True

    if username and username.lower() in WATCH_USERNAMES:
        return True

    return False


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        if not event.is_private:
            return

        sender = await event.get_sender()
        if not is_watched(sender):
            return

        name = getattr(sender, "first_name", None) or "Unknown"
        username = getattr(sender, "username", None)
        sender_id = getattr(sender, "id", None)
        text = event.raw_text or "[pesan non-teks]"

        notif = f"🔔 Pesan baru dari {name}"
        if username:
            notif += f" (@{username})"
        notif += f"\nID: {sender_id}\n\n{text[:1000]}"

        send_bot_notification(notif)
        print(f"Notif terkirim untuk sender_id={sender_id}")

    except Exception as e:
        print("Error saat memproses pesan:", repr(e))


async def main():
    print("Notifier aktif...")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
