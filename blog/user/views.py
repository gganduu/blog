from django.shortcuts import render
from django.http.response import HttpResponseBadRequest, HttpResponse, JsonResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from utils.response_code import RETCODE
import random
import re
from user.models import User
from libs.yuntongxun.sms import CCP

import logging
logger = logging.getLogger('blog')

# Create your views here.

def register(request):
    return render(request, 'user/register.html')

def change_captcha(request):
    uuid = request.GET.get('uuid')
    if uuid is None:
        return HttpResponseBadRequest('None UUID')
    text, img = captcha.generate_captcha()
    conn = get_redis_connection('default')
    conn.setex('img:' + str(uuid), 300, text)
    return HttpResponse(img, content_type='image/jpeg')

def get_sms(request):
    mobile = request.GET.get('mobile')
    image_code = request.GET.get('image_code')
    uuid = request.GET.get('uuid')
    if not all([mobile, image_code, uuid]):
        return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': 'Not enough params provided'})
    conn = get_redis_connection('default')
    text_saved = conn.get('img:'+str(uuid))
    if not text_saved:
        return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image code has run out of time'})
    try:
        conn.delete('img:'+str(uuid))
    except Exception as e:
        logger.error(e)
    if image_code.lower() != text_saved.decode().lower():
        return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image code is incompatible'})
    sms_code = random.randint(100000, 999999)
    conn.setex('sms:' + str(mobile), 300, sms_code)
    logger.info(sms_code)
    ccp = CCP()
    ccp.send_template_sms(18917526836, [sms_code, 5], 1)
    return JsonResponse({'code': RETCODE.OK})

def logon(request):
    mobile = request.POST.get('mobile')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    sms_code = request.POST.get('sms_code')
    if not all([mobile, password, password2, sms_code]):
        return HttpResponseBadRequest('Not enough 4 parameters provided')
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return HttpResponseBadRequest('Mobile number is invalid')
    if not re.match(r'[_\w]{8,20}', password):
        return HttpResponseBadRequest('Password must be composed by letters, numbers and _')
    if password != password2:
        return HttpResponseBadRequest('Confirm password is not compatible with password')
    conn = get_redis_connection('default')
    saved_sms_code = conn.get('sms:'+str(mobile))
    if saved_sms_code is None:
        return HttpResponseBadRequest('SMS code has run out of time')
    if saved_sms_code.decode() != sms_code:
        return HttpResponseBadRequest('Input wrong SMS code')
    try:
        User.objects.create_user(username=mobile, mobile=mobile, password=password)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Logon failed')
    return HttpResponse('Logon successfully')

