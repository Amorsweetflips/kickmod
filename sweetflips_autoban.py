import asyncio
from playwright.async_api import async_playwright
import json
import time
from collections import defaultdict

KICK_CHANNEL = "sweetflips"
DUPLICATE_THRESHOLD = 2
DUPLICATE_TIME_WINDOW = 5  # seconds

user_messages = defaultdict(list)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Load cookies
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(f"https://kick.com/{KICK_CHANNEL}/chatroom")
        print(f"[+] Navigated to chatroom: {KICK_CHANNEL}")

        while True:
            try:
                messages = await page.query_selector_all("div.chat-message")
                for message in messages[-10:]:
                    try:
                        username_elem = await message.query_selector("a.username")
                        message_elem = await message.query_selector("div.message")
                        username = (await username_elem.inner_text()).strip()
                        text = (await message_elem.inner_text()).strip()
                        now = time.time()

                        user_messages[username].append((text, now))
                        user_messages[username] = [
                            (msg, ts) for msg, ts in user_messages[username]
                            if now - ts <= DUPLICATE_TIME_WINDOW
                        ]

                        messages_text = [msg for msg, ts in user_messages[username]]
                        most_common = max(set(messages_text), key=messages_text.count)
                        count = messages_text.count(most_common)

                        if count >= DUPLICATE_THRESHOLD:
                            print(f"[SPAM DETECTED] Banning user: {username}")
                            chatbox = await page.query_selector("textarea.chat-input")
                            await chatbox.fill(f"/ban {username}")
                            await chatbox.press("Enter")
                            user_messages[username] = []
                            await asyncio.sleep(2)

                    except Exception:
                        continue

                await asyncio.sleep(2)

            except Exception as e:
                print(f"[ERROR]: {e}")
                await asyncio.sleep(5)

asyncio.run(run())
