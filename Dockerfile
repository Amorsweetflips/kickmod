# … earlier steps (FROM, COPY, RUN npm install, etc.)

# sanity check
RUN ls -al /usr/src/app

# now point to index.cjs
CMD ["node", "index.cjs"]
