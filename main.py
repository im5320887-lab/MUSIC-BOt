import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION = os.getenv("SESSION")

# Bot Client
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Assistant User Client
user = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# Voice Chat Client
call = PyTgCalls(user)


# === DOWNLOAD SONG ===
def download_audio(query):
    try:
        opts = {
            "format": "bestaudio/best",
            "outtmpl": "song.mp3",
            "quiet": True
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            return "song.mp3", info["entries"][0]["title"]
    except Exception as e:
        print("Error:", e)
        return None, None


# === COMMANDS ===
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("🔥 **Music Bot Online!**\nUse: `/play song name`")


@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("Gaana ka naam likh bhai…")

    query = " ".join(message.command[1:])
    msg = await message.reply(f"🔍 Searching **{query}** ...")

    file, title = download_audio(query)
    if not file:
        return await msg.edit("❌ Error downloading audio")

    chat_id = message.chat.id

    try:
        await call.join_group_call(
            chat_id,
            AudioPiped(file),
        )
        await msg.edit(f"🎶 Playing: **{title}**")
    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")


@app.on_message(filters.command("stop"))
async def stop(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("🛑 Music Stopped")


# === RUN ===
user.start()
call.start()
app.run()
