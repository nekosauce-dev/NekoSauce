#!/bin/bash

# Function to clean up and stop all processes
cleanup_and_stop() {
    echo "Stopping all processes..."
    kill -TERM $daphne_pid $dramatiq_worker_pid
}

# Trap the exit signals and call the cleanup function
trap cleanup_and_stop EXIT INT TERM

# Navigate to the app directory
cd /app

# Apply Django migrations
python manage.py migrate

# Start Daphne with multiple workers and binding address
daphne -b 0.0.0.0 -p 8000 nekosauce.asgi:application &
daphne_pid=$!

# Start Dramatiq worker
python manage.py rundramatiq --processes $BACKEND_DRAMATIQ_WORKERS --threads $BACKEND_DRAMATIQ_THREADS &
dramatiq_worker_pid=$!

# Wait for any of the processes to finish
wait -n

# Cleanup function will be called due to the trap
