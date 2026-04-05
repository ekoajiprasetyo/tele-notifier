import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = int(os.getenv("BOT_CHAT_ID"))

WATCH_IDS = {
    int(x.strip()) for x in os.getenv("WATCH_IDS", "").split(",")
    if x.strip()
}

WATCH_USERNAMES = {
    x.strip().lower().replace("@", "") for x in os.getenv("WATCH_USERNAMES", "").split(",")
    if x.strip()
}

SESSION_NAME = "main_account_session"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


def send_bot_notification(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": BOT_CHAT_ID,
            "text": text
        },
        timeout=15
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
        notif += f"\nID: {sender_id}\n\n{text}"

        send_bot_notification(notif)

    except Exception as e:
        print("Error:", e)


async def main():
    print("Notifier aktif...")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
