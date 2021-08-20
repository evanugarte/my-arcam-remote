FROM node:alpine as builder

WORKDIR /frontend

COPY website/package.json .

RUN npm install

COPY website/public public/

COPY website/src src/

COPY website/rollup.config.js .

RUN npm run build --production

FROM python:3.8.4-slim-buster

WORKDIR /app

RUN apt-get update

RUN yes | apt-get install curl git

COPY --from=builder /frontend/public/ /app/website/public

COPY requirements.txt .

COPY server.py .

COPY setup.sh .

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install "Flask[async]"

RUN ["/bin/bash", "./setup.sh"]

EXPOSE 5000

CMD ["python3", "server.py"]
