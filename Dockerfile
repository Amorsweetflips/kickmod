FROM node:18-slim

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --only=production

COPY . .

# sanity check: make sure index.js is here
RUN ls -al /usr/src/app

CMD ["node", "index.js"]
