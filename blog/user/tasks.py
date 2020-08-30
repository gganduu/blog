from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from django_redis import get_redis_connection

@shared_task
def sendmail(email):
    conn = get_redis_connection('default')
    conn.setex('start', 300, 'start send email to %s' % email)
    print('start send email to %s' % email)
    time.sleep(15)
    conn.setex('end', 300, 'success')
    print('success')
    return True