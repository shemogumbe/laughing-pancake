web: gunicorn app:app -b 0.0.0.0:$PORT --log-file - --access-logfile -  --preload -w 2
release: python manage.py db upgrade