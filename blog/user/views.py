from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.http.response import HttpResponseBadRequest, JsonResponse
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

class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        mobile = request.POST.get('mobile')
        passwd = request.POST.get('password')
        passwd2 = request.POST.get('password2')
        sms_code = request.POST.get('sms_code')
        if not all([mobile, passwd, passwd2, sms_code]):
            return HttpResponseBadRequest('code:'+str(RETCODE.NECESSARYPARAMERR))
        if not re.match(r'1[3-9]\d{9}', mobile):
            return HttpResponseBadRequest('code:'+str(RETCODE.MOBILEERR))
        if passwd != passwd2:
            return HttpResponseBadRequest('code:'+str(RETCODE.PWDERR))
        redis_conn = get_redis_connection('default')
        saved_sms_code = redis_conn.get('mob:'+str(mobile))
        if saved_sms_code.decode() != sms_code:
            return HttpResponseBadRequest('code:'+str(RETCODE.SMSCODERR))
        # save to mysql and redirect to index.html
        try:
            User.objects.create_user(username=mobile, password=passwd, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return HttpResponse('code:'+str(RETCODE.THROTTLINGERR))
        return HttpResponse('code:'+str(RETCODE.OK))

class ChangeImgCodeView(View):
    def get(self, request):
        uuid = request.GET.get('uuid')
        if uuid is None:
            return HttpResponseBadRequest('UUID is None')
        text, image = captcha.generate_captcha()
        # save image code to redis for authentication
        redis_conn = get_redis_connection('default')
        redis_conn.setex('img:'+str(uuid), 300, text)
        return HttpResponse(image, content_type='image/jpeg')

class SendSMSView(View):
    def get(self, request):
        uuid = request.GET.get('uuid')
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        # verify parameters
        if not all([uuid, mobile, image_code]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': 'Input parameters have problems'})
        redis_conn = get_redis_connection('default')
        saved_image_code = redis_conn.get('img:'+str(uuid))
        if saved_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image code has run out of time'})
        try:
            redis_conn.delete('img'+str(uuid))
        except Exception as e:
            logger.error(e)
        if saved_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image code is incompatible'})
        ccp = CCP()
        sms_code = random.randint(100000, 999999)
        ccp.send_template_sms(mobile, [sms_code, 5], 1)
        # save the sms code in redis for following register authentication
        redis_conn.setex('mob:'+str(mobile), 300, sms_code)
        return JsonResponse({'code': RETCODE.OK})


