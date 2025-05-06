import fs from 'fs/promises';
import path from 'path';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();
puppeteer.use(StealthPlugin());

const argv = yargs(hideBin(process.argv))
  .option('headful', {
    type: 'boolean',
    default: false,
    describe: 'Run with visible browser window'
  })
  .parse();

const CHANNEL_SLUG = process.env.CHANNEL_SLUG;
if (!CHANNEL_SLUG) {
  console.error('🔴  You must set CHANNEL_SLUG in your .env');
  process.exit(1);
}

const COOKIES_PATH = path.resolve(process.cwd(), 'cookies.json');

async function loadOrLogin(page) {
  try {
    const raw = await fs.readFile(COOKIES_PATH, 'utf8');
    const cookies = JSON.parse(raw);
    await page.setCookie(...cookies);
    console.log('🔒 Loaded cookies');
  } catch {
    console.log('🔐 No cookies found; please log in manually.');
    await page.goto(`https://kick.com/${CHANNEL_SLUG}`, { waitUntil: 'networkidle2' });
    console.log('▶️  After solving Cloudflare / login, press ENTER');
    await new Promise(r => process.stdin.once('data', r));
    const cookies = await page.cookies();
    await fs.writeFile(COOKIES_PATH, JSON.stringify(cookies, null, 2));
    console.log(`💾 Cookies saved to ${COOKIES_PATH}`);
  }
}

async function getChannelId(page) {
  // 1) Try meta tag
  try {
    await page.waitForSelector('meta[property="kick:channel_id"]', { timeout: 10_000 });
    const id = await page.$eval('meta[property="kick:channel_id"]', el => el.content);
    if (id) return id;
  } catch {}

  // 2) Fallback to Next.js page data
  await page.waitForSelector('script#__NEXT_DATA__', { timeout: 10_000 });
  const raw = await page.$eval('script#__NEXT_DATA__', el => el.textContent);
  const data = JSON.parse(raw);
  // adjust these paths if Kick changes their schema
  const possible =
    data?.props?.pageProps?.channel?.id ||
    data?.props?.initialState?.channel?.id ||
    data?.props?.pageProps?.channel?.channel_id;
  if (possible) return possible;

  throw new Error('Channel ID not found on page');
}

async function sendMessage(channelId, message) {
  const url = `https://kick.com/api/v1/channels/${channelId}/message`;
  const res = await axios.post(
    url,
    { content: message },
    { withCredentials: true }
  );
  if (res.status !== 200) throw new Error(`send failed: ${res.status}`);
}

(async () => {
  const browser = await puppeteer.launch({
    headless: !argv.headful,
    defaultViewport: null
  });
  const page = await browser.newPage();

  await loadOrLogin(page);
  await page.goto(`https://kick.com/${CHANNEL_SLUG}`, { waitUntil: 'networkidle2' });

  const channelId = await getChannelId(page);
  console.log(`✅  Channel ID = ${channelId}`);

  // example: send a message every 5 seconds
  setInterval(async () => {
    try {
      await sendMessage(channelId, 'Whats up happy people !!');
      console.log('📨 sent “Whats up happy people !!”');
    } catch (e) {
      console.error('✖ send error:', e.message);
    }
  }, 5_000);
})();
