FROM python:alpine

COPY . /app
WORKDIR /app

RUN apk update && apk --no-cache add gfortran openblas-dev

RUN pip install poetry
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN rm pyproject.toml
RUN pip install -r requirements.txt
