#!/bin/bash

# Function to clean up and stop all processes
cleanup_and_stop() {
    echo "Stopping all processes..."
    kill -TERM $gunicorn_pid $celery_worker_pids $celery_beat_pid
}

# Trap the exit signals and call the cleanup function
trap cleanup_and_stop EXIT INT TERM

# Navigate to the app directory
cd /app

# Apply Django migrations
python manage.py migrate

# Start Gunicorn with multiple workers and binding address
gunicorn -w $GUNICORN_WORKERS -b 0.0.0.0:8000 nekosauce.wsgi:application &
gunicorn_pid=$!

celery -A nekosauce purge -f

# Get the desired Celery concurrency from the environment variable
if [ -n "$CELERY_CONCURRENCY" ]; then
    celery_concurrency_option="-c $CELERY_CONCURRENCY"
else
    celery_concurrency_option=""
fi

# Start multiple Celery workers with gevent pool and specified concurrency
celery_worker_pids=()
for ((i=1; i<=$CELERY_WORKERS; i++)); do
    celery -A nekosauce worker -l INFO $celery_concurrency_option -n worker$i@nekosauce.org -P gevent -Q celery &
    celery_worker_pids+=($!)

    sleep 10
done

# Start Celery beat scheduler with DatabaseScheduler
celery -A nekosauce beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery_beat_pid=$!

# Wait for any of the processes to finish
wait -n

# Cleanup function will be called due to the trap
