FROM arm32v7/node:16-alpine3.11 as builder

WORKDIR /frontend

COPY package.json ./

COPY package-lock.json ./

RUN npm install

COPY public public/

COPY src src/

COPY rollup.config.js .

RUN npm run build --production

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /frontend/public/ /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
