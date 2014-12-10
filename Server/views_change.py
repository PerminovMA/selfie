__author__ = 'Mihail'

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from tools import make_error, token_update
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from gcm.models import Device
from models import User
from properties import MAX_FILE_SIZE
from django.db import IntegrityError


@csrf_exempt
def change_user_info_request(request): # deprecated 06.12.14
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
    device_id = None if request.POST.get("device_id") is None or request.POST.get("device_id") == '' else request.POST.get("device_id").__str__().strip()
    gcm_reg_id = None if request.POST.get("gcm_reg_id") is None or request.POST.get("gcm_reg_id") == '' else request.POST.get("gcm_reg_id").__str__().strip()
    country = None if request.POST.get("country") is None or request.POST.get("country") == '' else request.POST.get("country").__str__().strip()
    city = None if request.POST.get("city") is None or request.POST.get("city") == '' else request.POST.get("city").__str__().strip()
    app_version = None if request.POST.get("app_version") is None or request.POST.get("app_version") == '' else request.POST.get("app_version").__str__().strip()

    if user_id is None or token is None:
        return HttpResponse(make_error(explanation="missing required argument", errorid="1", functionName="change_user_info_request"))

    try:
        user = User.objects.select_related('token', 'gcm_device').get(id = user_id)
        if token != user.token.token:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id, functionName="change_user_info_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", functionName="change_user_info_request"))

    try:
        if device_id is not None and gcm_reg_id is not None:
            if user.gcm_device is None:
                gcm_device = Device.objects.create(reg_id = gcm_reg_id, name = user.email, is_active = True, dev_id = device_id)
                user.gcm_device = gcm_device
                # user.save(update_fields=['gcm_device', 'lastActivity'])
            else:
                user.gcm_device.dev_id = device_id
                user.gcm_device.reg_id = gcm_reg_id
                user.gcm_device.save()
    except IntegrityError as err_obj:
        return HttpResponse(make_error(explanation="IntegrityError: " + err_obj.message, errorid="39", functionName="change_user_info_request"))

    if country is not None:
        user.country = country
    if city is not None:
        user.city = city
    if app_version is not None:
        user.app_version = app_version

    user.save()

    return HttpResponse('{"report" : "success", "explanation": "User information updated", "token": "' + token_update(user) + '"}')


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def change_avatar_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
    photo_file = None if request.FILES.get("file") is None else request.FILES.get("file")
    status = None if request.POST.get("status") is None else request.POST.get("status").encode("utf-8").strip()

    if user_id is None or user_id == '' or photo_file is None or token is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", functionName="change_avatar_request"))

    if photo_file.size > MAX_FILE_SIZE:
        return HttpResponse(
            make_error(explanation="file too large", errorid="38", functionName="change_avatar_request"))

    try:
        user = User.objects.select_related('token').get(id=user_id)
        if token == user.token.token:
            if user.avatar.name == '':
                user.avatar = photo_file
                user.status = unicode(status, "utf-8")
                if user.user_state != User.TYPE_OF_USER_STATE[1][0]:
                    user.user_state = User.TYPE_OF_USER_STATE[2][0]
                user.save(update_fields=['avatar', 'lastActivity', 'status'])
                return HttpResponse(
                    '{"report" : "success", "explanation": "avatar has been changed", "token": "' + token_update(
                        user) + '", "user_id": "' + str(user.id) + '"}')
            else:
                user.avatar.delete()
                user.avatar = photo_file
                user.status = unicode(status, "utf-8")
                if user.user_state != User.TYPE_OF_USER_STATE[1][0]:
                    user.user_state = User.TYPE_OF_USER_STATE[2][0]
                user.save()
                return HttpResponse(
                    '{"report" : "success", "explanation": "avatar has been changed", "token": "' + token_update(
                        user) + '", "user_id": "' + str(user.id) + '"}')
        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="change_avatar_request"))

        return HttpResponse(str(user.avatar is None))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", functionName="change_avatar_request"))
