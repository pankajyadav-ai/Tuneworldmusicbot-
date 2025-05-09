
import os
import logging
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = Client("song_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Logging
logging.basicConfig(level=logging.INFO)

# Dictionary to store premium users
premium_users = set()

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        """
Welcome to TuneWorld Music Bot!
Use /song <name> to download a song.
To get premium access, type /premium
        """
    )

@app.on_message(filters.command("premium"))
def premium(client, message):
    message.reply_text(
        """
Premium Plan: Rs. 49/month
Pay via UPI: 79008190211@axl
After payment, send screenshot and use /verify
        """
    )

@app.on_message(filters.command("verify"))
def verify(client, message):
    message.reply_text("Please send your payment screenshot here. Admin will verify soon.")
    client.send_message(ADMIN_ID, f"User @{message.from_user.username} ({message.from_user.id}) requested premium verification.")

@app.on_message(filters.command("song"))
def song(client, message):
    if message.from_user.id not in premium_users:
        message.reply_text("This feature is only for premium users. Use /premium to upgrade.")
        return

    query = message.text.split(None, 1)
    if len(query) < 2:
        message.reply_text("Please provide a song name after /song")
        return

    search = query[1]
    msg = message.reply_text("Searching for your song...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            title = info['title']
            url = info['webpage_url']
            ydl.download([url])
            filename = f"{title}.mp3"

        client.send_audio(message.chat.id, audio=open(filename, "rb"), title=title)
        os.remove(filename)
        msg.delete()

    except Exception as e:
        msg.edit(f"Error: {e}")

# Admin command to add premium users
@app.on_message(filters.command("addpremium") & filters.user(ADMIN_ID))
def add_premium(client, message):
    try:
        user_id = int(message.text.split()[1])
        premium_users.add(user_id)
        message.reply_text(f"User {user_id} added to premium list.")
    except:
        message.reply_text("Usage: /addpremium <user_id>")

app.run()
