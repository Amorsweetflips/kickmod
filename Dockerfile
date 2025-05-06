FROM node:18-slim

WORKDIR /usr/src/app

# install Chromium deps
RUN apt-get update && apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libcups2 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 \
    libpangocairo-1.0-0 libpango1.0-0 libnss3 libxss1 libxtst6 \
    fonts-liberation libappindicator3-1 xdg-utils --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install --production

COPY . .

CMD ["node", "kick-puppeteer-bot.js"]
