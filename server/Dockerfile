FROM python:3.9.6-slim-buster

WORKDIR /app

RUN apt-get update

RUN yes | apt-get install curl git

COPY requirements.txt .

ENV MULTIDICT_NO_EXTENSIONS=1

ENV YARL_NO_EXTENSIONS=1

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install "Flask[async]"

COPY setup.sh .

RUN ["/bin/bash", "./setup.sh"]

COPY *.py ./

EXPOSE 5000

ENTRYPOINT ["python", "server.py"]
