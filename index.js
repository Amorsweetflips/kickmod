const puppeteer = require('puppeteer');

(async () => {
  console.log('🟢 Bot starting…');
  try {
    const browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    const page = await browser.newPage();

    console.log('🔵 Logging in…');
    await page.goto('https://kick.com/login', { waitUntil: 'networkidle2' });
    await page.type('input[name="login"]', process.env.KICK_USER, { delay: 50 });
    await page.type('input[name="password"]', process.env.KICK_PASS, { delay: 50 });
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('✅ Logged in');

    const chatUrl = process.env.KICK_CHAT_URL || 'https://kick.com/sweetflips';
    console.log('🔵 Going to chat:', chatUrl);
    await page.goto(chatUrl, { waitUntil: 'networkidle2' });

    await page.waitForSelector('.chat-message', { timeout: 30000 });
    await page.screenshot({ path: 'debug_screenshot.png' });
    console.log('✅ Screenshot done');

    await browser.close();
    console.log('🟢 Bot finished');
  } catch (err) {
    console.error('🔴 Crash:', err);
    process.exit(1);
  }
})();
