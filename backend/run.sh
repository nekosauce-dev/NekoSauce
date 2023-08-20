cd /app

python manage.py migrate

gunicorn -w $WORKERS -b 0.0.0.0:8000 nekosauce.wsgi:application &
celery -A nekosauce worker -l INFO -P gevent -Q default -c 4 &
celery -A nekosauce beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &

wait -n

exit $?
