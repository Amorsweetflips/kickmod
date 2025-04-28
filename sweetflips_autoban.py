
# SweetflipsBot Auto-Banner (Chatroom Version) - FINAL LOGIN FIX
# By Amor Munoz - Instant Ban Kick Spammers

import time
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
options.add_argument("--headless=new")
options.binary_location = "/usr/bin/chromium"

# Track messages
user_messages = defaultdict(list)

def login(driver):
    driver.get("https://kick.com/login")
    wait = WebDriverWait(driver, 15)

    email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="email"]')))
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))

    email_input.send_keys(KICK_USERNAME)
    password_input.send_keys(KICK_PASSWORD)

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Log In")]')))
    login_button.click()
    print("[+] Logged in successfully.")
    time.sleep(5)

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
