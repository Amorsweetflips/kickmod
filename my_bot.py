import os
import asyncio
from kickbot import KickBot
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

EMAIL   = os.getenv("KICK_EMAIL")
PASSWD  = os.getenv("KICK_PASSWORD")
CHANNEL = os.getenv("STREAMER_CHANNEL", "sweetflips")

async def main():
    # Initialize the bot with positional args
    bot = KickBot(EMAIL, PASSWD)
    # Tell it which channel to join
    bot.set_streamer(CHANNEL)

    # Send a welcome message when connected
    await bot.send_message("🤖 Bot is now online! Type !ban <user> or !timeout <user> to moderate.")

    # Register a command handler for !timeout
    @bot.on_message
    async def handle_commands(message):
        text = message.content.lower()
        if text.startswith("!timeout "):
            target = text.split()[1]
            await bot.timeout(target)
            print(f"⏱️ Timed out {target}")
        elif text.startswith("!ban "):
            target = text.split()[1]
            await bot.ban(target)
            print(f"⛔ Banned {target}")

    # Run until interrupted
    await bot.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
