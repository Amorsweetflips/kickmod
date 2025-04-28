
# SweetflipsBot Auto-Banner (Chatroom Version)
# By Amor Munoz - Instant Ban Kick Spammers

import time
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# CONFIGURATION
KICK_USERNAME = "Sweetflipsbot"
KICK_PASSWORD = "TheHype01!"
KICK_CHANNEL = "sweetflips"
DUPLICATE_THRESHOLD = 2
DUPLICATE_TIME_WINDOW = 5  # seconds

# Selenium Setup
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

# Track messages
user_messages = defaultdict(list)

def login(driver):
    driver.get("https://kick.com/login")
    time.sleep(2)
    driver.find_element(By.NAME, "email").send_keys(KICK_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(KICK_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]").click()
    time.sleep(5)
    print("[+] Logged in successfully.")

def navigate_to_chatroom(driver):
    driver.get(f"https://kick.com/{KICK_CHANNEL}/chatroom")
    time.sleep(5)
    print(f"[+] Navigated to chatroom: {KICK_CHANNEL}/chatroom")

def detect_and_ban(driver):
    while True:
        try:
            messages = driver.find_elements(By.CSS_SELECTOR, "div.chat-message")
            for message in messages[-10:]:
                try:
                    username_elem = message.find_element(By.CSS_SELECTOR, "a.username")
                    message_elem = message.find_element(By.CSS_SELECTOR, "div.message")
                    username = username_elem.text.strip()
                    text = message_elem.text.strip()
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
                        chatbox = driver.find_element(By.CSS_SELECTOR, "textarea.chat-input")
                        chatbox.send_keys(f"/ban {username}")
                        chatbox.send_keys(Keys.ENTER)
                        user_messages[username] = []  # Clear after banning
                        time.sleep(2)

                except Exception:
                    continue

            time.sleep(2)

        except Exception as e:
            print(f"[ERROR]: {e}")
            time.sleep(5)

def main():
    driver = uc.Chrome(options=options)
    login(driver)
    navigate_to_chatroom(driver)
    detect_and_ban(driver)

if __name__ == "__main__":
    main()
