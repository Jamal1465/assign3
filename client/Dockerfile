FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Clean optional dependency issues if needed
RUN rm -rf node_modules package-lock.json && npm install

RUN npm run build

RUN npm install -g serve

CMD ["serve", "-s", "dist"]
