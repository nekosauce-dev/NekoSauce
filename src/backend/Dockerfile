FROM python:slim

COPY . /app
WORKDIR /app

RUN pip install poetry
RUN poetry export --without-hashes --format=requirements.txt --output=requirements.txt
RUN rm pyproject.toml
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
RUN mv /app/static /static
RUN chmod 755 /app/run.sh
