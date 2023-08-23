#!/bin/bash

# Function to clean up and stop all processes
cleanup_and_stop() {
    echo "Stopping all processes..."
    kill -TERM $gunicorn_pid $celery_worker_pid $celery_beat_pid
}

# Trap the exit signals and call the cleanup function
trap cleanup_and_stop EXIT INT TERM

# Navigate to the app directory
cd /app

# Apply Django migrations
python manage.py migrate

# Start Gunicorn with specified workers and binding address
gunicorn -w $WORKERS -b 0.0.0.0:8000 nekosauce.wsgi:application &
gunicorn_pid=$!

# Start Celery worker with gevent pool and concurrency of 4
celery -A nekosauce worker -l INFO -P gevent -c 4 &
celery_worker_pid=$!

# Start Celery beat scheduler with DatabaseScheduler
celery -A nekosauce beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery_beat_pid=$!

# Wait for any of the processes to finish
wait -n

# Cleanup function will be called due to the trap