# 1. Base image
FROM node:18-slim

# 2. Create app dir
WORKDIR /usr/src/app

# 3. Copy package files & install deps
COPY package*.json ./
RUN npm install --only=production

# 4. Copy all your source in
COPY . .

# 5. Sanity check: list files in workdir
RUN ls -al /usr/src/app

# 6. Run your CommonJS entrypoint
CMD ["node", "index.cjs"]
