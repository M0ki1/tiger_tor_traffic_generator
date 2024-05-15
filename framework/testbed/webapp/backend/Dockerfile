FROM node:16.18.1-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .

EXPOSE 4000

CMD ["npm", "run", "migrate:prod"]
#CMD ["sleep", "10000000000"]