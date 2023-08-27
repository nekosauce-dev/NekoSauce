#!/bin/bash

# Function to clean up and stop all processes
cleanup_and_stop() {
    echo "Stopping all processes..."
    kill -TERM $gunicorn_pid $dramatiq_worker_pid
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


# Start Dramatiq worker
python manage.py rundramatiq --processes $DRAMATIQ_WORKERS --threads $DRAMATIQ_THREADS --use-gevent --skip-logging &
dramatiq_worker_pid=$!

# Wait for any of the processes to finish
wait -n

# Cleanup function will be called due to the trap
