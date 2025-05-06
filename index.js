const puppeteer = require('puppeteer');

(async () => {
  console.log('🟢 Bot starting…');
  try {
    // launch headless with necessary flags for container env
    const browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    const page = await browser.newPage();

    // 1️⃣ Log in
    console.log('🔵 Going to login page…');
    await page.goto('https://kick.com/login', { waitUntil: 'networkidle2' });

    // type credentials from Railway env
    await page.type('input[name="login"]', process.env.KICK_USER, { delay: 50 });
    await page.type('input[name="password"]', process.env.KICK_PASS, { delay: 50 });
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('✅ Logged in as', process.env.KICK_USER);

    // 2️⃣ Go to chatroom
    const chatUrl = process.env.KICK_CHAT_URL || 'https://kick.com/YOUR_CHATROOM_URL';
    console.log('🔵 Navigating to chat:', chatUrl);
    await page.goto(chatUrl, { waitUntil: 'networkidle2' });
    
    // 3️⃣ Wait for chat to load & screenshot
    await page.waitForSelector('.chat-message', { timeout: 30000 });
    await page.screenshot({ path: 'debug_screenshot.png' });
    console.log('✅ Screenshot taken: debug_screenshot.png');

    await browser.close();
    console.log('🟢 Bot finished successfully');
  } catch (err) {
    console.error('🔴 Fatal error:', err);
    process.exit(1);
  }
})();
