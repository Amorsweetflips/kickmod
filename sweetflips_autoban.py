
import os
import subprocess
import undetected_chromedriver.v2 as uc

def main():
    # Clean up old Xvfb lock if it exists
    if os.path.exists('/tmp/.X99-lock'):
        os.remove('/tmp/.X99-lock')

    # Start Xvfb
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'])
    os.environ["DISPLAY"] = ":99"

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # Important for servers

    # You can specify the Chrome path if necessary
    driver = uc.Chrome(options=options)

    driver.get("https://www.google.com")
    print("Title is:", driver.title)
    driver.quit()

if __name__ == "__main__":
    main()
