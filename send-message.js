import puppeteer from 'puppeteer';

(async () => {
  console.log('🟢 Bot starting…');

  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  try {
    await page.goto('https://kick.com');

    // Example: wait for element to ensure page loaded
    await page.waitForSelector('body');

    console.log('✅ Kick page loaded successfully!');

    // Your bot logic here (e.g., send messages, interact with elements)

  } catch (error) {
    console.error('🔴 Error:', error);
  } finally {
    await browser.close();
    console.log('🔵 Bot completed and closed browser');
  }
})();