import asyncio
from playwright.async_api import async_playwright
import json
import time
from collections import defaultdict

# CONFIGURATION
KICK_CHANNEL = "sweetflips"
KICK_EMAIL = "your_email@example.com"
KICK_PASSWORD = "yourpassword"
DUPLICATE_THRESHOLD = 2
DUPLICATE_TIME_WINDOW = 5  # seconds

user_messages = defaultdict(list)

async def login_if_needed(page):
    try:
        email_field = await page.query_selector('input[name="email"]')
        password_field = await page.query_selector('input[name="password"]')

        if email_field and password_field:
            print("[+] Login form detected, logging in automatically...")
            await email_field.fill(KICK_EMAIL)
            await password_field.fill(KICK_PASSWORD)

            login_button = await page.query_selector('button[type="submit"]')
            if login_button:
                await login_button.click()
                await page.wait_for_selector('header', timeout=30000)
                print("[+] Logged in successfully!")
        else:
            print("[+] Already logged in — skipping login.")
    except Exception as e:
        print(f"[Login Detection Error]: {e}")

async def run_bot():
    async with async_playwright() as p:
        print("[+] Launching Chromium browser...")
        browser = await p.chromium.launch(headless=True, timeout=10000)
        print("[+] Browser launched!")

        context = await browser.new_context()
        page = await context.new_page()

        print("[+] Going to Kick login page...")
        await page.goto("https://kick.com/login")
        print("[+] Kick login page opened!")

        await login_if_needed(page)

        print("[+] Navigating to sweetflips chatroom...")
        await page.goto(f"https://kick.com/{KICK_CHANNEL}/chatroom")
        await asyncio.sleep(5)

        # Try to open chat if it's not visible yet
        try:
            chat_input = await page.query_selector('textarea.chat-input')
            if not chat_input:
                print("[!] Chat input not found — trying to open chat manually...")
                open_chat_button = await page.query_selector('button:has-text("Join Chat")')
                if not open_chat_button:
                    open_chat_button = await page.query_selector('button:has-text("Expand Chat")')
                if open_chat_button:
                    await open_chat_button.click()
                    print("[+] Clicked chat open button, waiting...")
                    await asyncio.sleep(5)
                else:
                    print("[!] No chat open button found, maybe already in chat or chat restricted.")

            await page.wait_for_selector('textarea.chat-input', timeout=30000)
            print("[+] Chat input is ready!")

        except Exception as e:
            print(f"[Chat Opening Error]: {e}")
            await asyncio.sleep(60)

        print("[+] Bot is now monitoring the chat!")

        while True:
            try:
                messages = await page.query_selector_all("div.chat-message")
                if messages:
                    for message in messages[-10:]:
                        try:
                            username_elem = await message.query_selector("a.username")
                            message_elem = await message.query_selector("div.message")

                            if not username_elem or not message_elem:
                                continue

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
                                if chatbox:
                                    await chatbox.fill(f"/ban {username}")
                                    await chatbox.press("Enter")
                                    user_messages[username] = []
                                    await asyncio.sleep(2)

                        except Exception as inner_error:
                            print(f"[Inner Error]: {inner_error}")
                            continue

                await asyncio.sleep(2)

            except Exception as outer_error:
                print(f"[Outer Error]: {outer_error}")
                await asyncio.sleep(5)

async def main():
    while True:
        try:
            await run_bot()
        except Exception as e:
            print(f"[FATAL ERROR] Restarting bot in 10 seconds... Reason: {e}")
            await asyncio.sleep(10)

asyncio.run(main())
