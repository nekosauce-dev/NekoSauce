FROM python:alpine

COPY . /app
WORKDIR /app

RUN pip install poetry
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN pip install -r requirements.txt