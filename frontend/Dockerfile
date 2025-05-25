FROM node:22-alpine3.21

WORKDIR /app

COPY ./frontend /app

RUN npm install

CMD [ "npm", "run", "build-only", "--", "--outDir", "/app/dist" ]
