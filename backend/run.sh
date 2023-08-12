cd /app

python manage.py migrate

gunicorn -w 4 -b 0.0.0.0:8080 nekosauce.wsgi:application
