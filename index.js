// kick-puppeteer-bot.js
const fs = require('fs');
const path = require('path');
const puppeteerExtra = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteerExtra.use(StealthPlugin());

// Change this if your Chrome is installed elsewhere
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

(async () => {
  const COOKIE_FILE = path.resolve(__dirname, 'cookies.json');
  const CONFIG = {
    streamerChannel: 'sweetflips',
    initialMessage:  'Hi there sweetflips',
  };

  const firstRun = !fs.existsSync(COOKIE_FILE);
  console.log(`🚀 Launching browser (${firstRun ? 'headful' : 'headless'})...`);

  const browser = await puppeteerExtra.launch({
    headless: !firstRun,
    executablePath: CHROME_PATH,
    defaultViewport: null,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      firstRun ? null : '--headless=new',
      '--window-size=1920,1080'
    ].filter(Boolean),
  });
  const [page] = await browser.pages();

  if (firstRun) {
    // ─── FIRST RUN: MANUAL LOGIN ───────────────────────────────────────────────
    await page.goto('https://kick.com', { waitUntil: 'networkidle2' });
    console.log('🔐 Please manually:');
    console.log('   • Accept any cookie banner');
    console.log('   • Click profile icon → Log In');
    console.log('   • Enter email/password');
    console.log('   • Solve Cloudflare/2FA if prompted');
    console.log('🛑 Once you see your avatar, press ENTER to save session cookies.');

    process.stdin.resume();
    await new Promise(r => process.stdin.once('data', r));
    process.stdin.pause();

    const cookies = await page.cookies();
    fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
    console.log(`💾 Cookies saved to cookies.json`);
    console.log('✅ First-run complete. Re-run headless to start the bot:');
    console.log('   node kick-puppeteer-bot.js');
    await browser.close();
    process.exit(0);
  }

  // ─── SUBSEQUENT RUNS: HEADLESS BOT ─────────────────────────────────────────
  const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
  await page.setCookie(...cookies);
  console.log('🔒 Loaded cookies; skipping login.');

  // Navigate to your channel page
  console.log(`🌐 Navigating to /${CONFIG.streamerChannel}…`);
  await page.goto(`https://kick.com/${CONFIG.streamerChannel}`, { waitUntil: 'networkidle2' });

  // Fetch channel ID via API (using your authenticated cookies)
  console.log('📥 Fetching channel ID from API…');
  const channelData = await page.evaluate(async channel => {
    const url = `https://kick.com/api/v1/channels/${channel}`;
    const res = await fetch(url, {
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error(`API fetch failed: ${res.status}`);
    return res.json();
  }, CONFIG.streamerChannel);

  const channelId = channelData.id;
  console.log(`[✅] Channel ID: ${channelId}`);

  // Inject WebSocket chat client and send the initial message
  console.log('🤖 Injecting chat WebSocket and sending initial message…');
  await page.evaluate((cid, msg) => {
    const ws = new WebSocket('wss://chat.kick.com');
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({
        event: 'pusher:subscribe',
        data: { auth: '', channel: `chatrooms.${cid}.v2` }
      }));
      setTimeout(() => {
        ws.send(JSON.stringify({
          event: 'message.send',
          data: { content: msg, chatroom_id: cid }
        }));
      }, 1000);
    });
    ws.addEventListener('message', ev => console.log('CHAT_MSG:' + ev.data));
    window.__BOT_WS__ = ws;
  }, channelId, CONFIG.initialMessage);

  // Listen for moderation commands (!timeout, !ban)
  console.log('🎧 Listening for !timeout and !ban commands…');
  page.on('console', async msg => {
    const text = msg.text();
    if (!text.startsWith('CHAT_MSG:')) return;
    const { event, data } = JSON.parse(text.slice(9));
    if (event !== 'message.send') return;
    const content = data.content.toLowerCase();
    const user    = data.sender.username;

    if (content.startsWith('!timeout ')) {
      const target = content.split(' ')[1];
      console.log(`⏱️ Timing out ${target}…`);
      await moderate(page, CONFIG.streamerChannel, target, 'Timeout');
    }
    if (content.startsWith('!ban ')) {
      const target = content.split(' ')[1];
      console.log(`⛔ Banning ${target}…`);
      await moderate(page, CONFIG.streamerChannel, target, 'Ban');
    }
  });

  async function moderate(page, channel, username, action) {
    await page.goto(`https://kick.com/${channel}`, { waitUntil: 'networkidle2' });
    const frame = page.frames().find(f => f.url().includes('kick.com/chat'));
    await frame.waitForSelector(`[data-username="${username}"]`);
    const el = await frame.$(`[data-username="${username}"]`);
    await el.click({ button: 'right' });
    await frame.click(`text="${action}"`);
    if (action === 'Ban') {
      await page.waitForTimeout(500);
      await frame.click('text="Confirm"');
    }
    console.log(`✅ ${action} executed on ${username}`);
  }

  console.log('✅ Bot is now running headless!');
})();
