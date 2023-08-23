FROM python:slim

COPY . /app
WORKDIR /app

RUN pip install poetry && \
    poetry export --without-hashes --format=requirements.txt --output=requirements.txt && \
    rm pyproject.toml && \
    pip install -r requirements.txt && \
    python manage.py collectstatic --noinput && \
    mv /app/static /static && \
    chmod 755 /app/run.sh
