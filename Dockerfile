# 1. Base image
FROM node:18-alpine

# 2. Create app dir
WORKDIR /usr/src/app

# 3. Copy package files & install deps
COPY package*.json ./
RUN npm install --production

# 4. Copy all your bot code in
COPY . .

# 5. Expose if needed (you probably don’t)
# EXPOSE 8080

# 6. Kick-off with the correct entrypoint
CMD ["node", "kick-puppeteer-bot.js"]
