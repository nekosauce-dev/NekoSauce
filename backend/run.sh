cd /app

python manage.py migrate

gunicorn -w $WORKERS -b 0.0.0.0:8000 nekosauce.wsgi:application &
celery -A nekosauce beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &

wait -n

exit $?
