#!/bash/sh

# django
gunicorn -c /home/onii/conf/gunicorn.conf.py onii.wsgi:application

# task
python /home/onii/jobs/cron.py

# cluster
python /home/onii/manage.py qcluster

# nginx
#/usr/sbin/nginx -g 'daemon off;
