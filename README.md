Celery POC
======================

Step to start the flask application

1. Install requirements.txt with pip
2. Run Flask instance with $ python celery_flask.py
3. Run Celery workers $ celery worker -A celery_flask.celery_app --loglevel=info
4. Keep calm and run asynchronously

Test script is include to test the integration workflow
