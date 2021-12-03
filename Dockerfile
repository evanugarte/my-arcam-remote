FROM arm32v7/node:16-alpine3.11 as builder

WORKDIR /frontend

COPY website/package.json .

RUN npm install

COPY website/public public/

COPY website/src src/

COPY website/rollup.config.js .

RUN npm run build --production

FROM arm32v7/python:3.9.6-slim-buster

WORKDIR /app

RUN apt-get update

RUN yes | apt-get install curl git

COPY --from=builder /frontend/public/ /app/website/public

COPY server/requirements.txt .

COPY server/setup.sh .

ENV MULTIDICT_NO_EXTENSIONS=1

ENV YARL_NO_EXTENSIONS=1

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install "Flask[async]"

RUN ["/bin/bash", "./setup.sh"]

COPY server/server.py .

EXPOSE 5000

CMD ["python3", "server.py"]
