# use a Chrome-friendly base
FROM node:18-slim

WORKDIR /usr/src/app

# install only prod deps
COPY package*.json ./
RUN npm install --only=production

# copy everything (including your bot script)
COPY . .

# sanity check: list files in workdir at build-time
RUN ls -al /usr/src/app

# launch your bot
CMD ["node", "kick-puppeteer-bot.js"]
