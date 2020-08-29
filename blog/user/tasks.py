from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time

@shared_task
def sendmail(email):
    print('start send email to %s' % email)
    time.sleep(15)
    print('success')
    return True