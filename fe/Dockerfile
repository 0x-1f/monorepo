FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

RUN npm install -g vite

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]