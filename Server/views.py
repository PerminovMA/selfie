# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tools import check_if_email_exists, make_error, get_new_token, token_update, remove_messages
from models import User, Message, Review
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
from django.utils import timezone
from datetime import timedelta
from gcm.models import Device
from django.conf import settings
from django.db import IntegrityError
from properties import MAX_FILE_SIZE
from django.db.models import F

#@ratelimit(block=True, rate='50/h')
@csrf_exempt
def check_email_exists_request(request):
    email = None if request.POST.get("email") is None else request.POST.get("email").__str__().strip()

    if email is None:
        return HttpResponse(
            make_error(explanation="missing requirement argument", errorid="1", functionName="check_email_exists"))
    try:
        user = User.objects.select_related('token').get(email=email)
        return HttpResponse(
            '{"report": "success", "explanation": "email already exists", "match": "true", "user_id": "' + str(
                user.id) + '", "token": "' + str(user.token.token) + '", "sex": "' + user.sex + '", "name":"' + user.name + '", "avatar":"' + (user.avatar.url if user.avatar else "None") + '", "age": "' + user.age + '", "status": "' + user.status + '"}')
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse('{"report": "success", "explanation": "email not exists", "match": "false"}')


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def add_user_request(request):
    email = None if request.POST.get("email") is None else request.POST.get("email").__str__().strip()
    # sex format "M" or "F"
    sex = None if request.POST.get("sex") is None else request.POST.get("sex").__str__().strip()
    age_range = None if request.POST.get("age_range") is None else request.POST.get("age_range").__str__().strip()
    name = None if request.POST.get("name") is None else request.POST.get("name").encode("utf-8").strip()
    country = None if request.POST.get("country") is None else request.POST.get("country").__str__().strip()
    city = None if request.POST.get("city") is None else request.POST.get("city").__str__().strip()

    photo_file = None if request.FILES.get("file") is None else request.FILES.get("file")
    status = None if request.POST.get("status") is None else request.POST.get("status").encode("utf-8").strip()
    if photo_file is None or status is None:
        return HttpResponse(make_error(explanation="missing required argument", errorid="1", functionName="add_user"))
    if photo_file.size > MAX_FILE_SIZE:
        return HttpResponse(
            make_error(explanation="file too large", errorid="38", functionName="add_user"))

    if request.POST.get("gcm_reg_id") is None or request.POST.get("gcm_reg_id") is "" or request.POST.get("device_id") is None or request.POST.get("device_id") is "":
        gcm_reg_id = None
    else:
        gcm_reg_id = request.POST.get("gcm_reg_id").__str__().strip()
        device_id = request.POST.get("device_id").__str__().strip()

    if sex is None or age_range is None or email is None or name is None:
        return HttpResponse(make_error(explanation="missing required argument", errorid="1", functionName="add_user"))

    if len(name) < 1 or len(name) > 25:
        return HttpResponse(make_error(explanation="username length is poor", errorid="37", functionName="add_user"))

    if (country is not None and len(country) == 0) or (city is not None and len(city) == 0):
        return HttpResponse(
            make_error(explanation="country or city is too short", errorid="37", functionName="add_user"))

    sex = sex.upper()
    if sex != User.MALE and sex != User.FEMALE:
        return HttpResponse(make_error(explanation="bad format in sex field", errorid="14", functionName="add_user"))

    # age_range format '1' or '2' or '3'
    if age_range != User.AGE_RANGE_1 and age_range != User.AGE_RANGE_2 and age_range != User.AGE_RANGE_3:
        return HttpResponse(
            make_error(explanation="bad format in age_range field", errorid="14", functionName="add_user"))

    if check_if_email_exists(email):
        return HttpResponse(
            make_error(explanation="user with that email already exists", errorid="15", functionName="add_user"))

    try:
        gcm_device = None if gcm_reg_id is None else Device.objects.create(reg_id = gcm_reg_id, name = email, is_active = True, dev_id = device_id)
    except IntegrityError as err_obj:
        return HttpResponse(
            make_error(explanation="IntegrityError: " + err_obj.message, errorid="39", functionName="add_user"))

    current_token = get_new_token()

    u = User(name=unicode(name, "utf-8"), email=email, age=age_range, sex=sex, status=unicode(status, "utf-8"), avatar=photo_file, token=current_token, country=country, city=city, gcm_device=gcm_device)
    u.save()
    return HttpResponse(
        '{"report" : "success", "explanation": "user has been added", "token": "' + current_token.token.__str__() + '", "user_id": "' + str(
            u.id) + '"}')


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
                user.save(update_fields=['avatar', 'lastActivity', 'status'])
                return HttpResponse(
                    '{"report" : "success", "explanation": "avatar has been changed", "token": "' + token_update(
                        user) + '", "user_id": "' + str(user.id) + '"}')
            else:
                user.avatar.delete()
                user.avatar = photo_file
                user.status = unicode(status, "utf-8")
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


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def send_message_request(request):
    from_user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    to_user_id = None if request.POST.get("to_user_id") is None else request.POST.get("to_user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
    photo_file = None if request.FILES.get("photo_file") is None else request.FILES.get("photo_file")
    preview_file = None if request.FILES.get("preview_file") is None else request.FILES.get("preview_file")
    text = '' if request.POST.get("text") is None else request.POST.get("text").encode("utf-8").strip()
    # if the message is sent in response
    answer_for_mes_id = None if request.POST.get("message_id") is None else request.POST.get("message_id").__str__().strip()

    if from_user_id is None or from_user_id == '' or photo_file is None or token is None or to_user_id is None or to_user_id == '' or preview_file is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", functionName="send_message_request"))

    # this block temproly commented
    #if from_user_id == to_user_id:
    #    return HttpResponse(
    #        make_error(explanation="from_user may not be = to_user", errorid="?", functionName="send_message_request"))

    if photo_file.size > MAX_FILE_SIZE or preview_file.size > MAX_FILE_SIZE:
        return HttpResponse(
            make_error(explanation="file too large", errorid="38", functionName="send_message_request"))

    try:
        from_user = User.objects.defer('id', 'count_outgoing_messages', 'lastActivity').select_related('token').get(id = from_user_id)
        to_user = User.objects.defer('id', 'count_incoming_messages').select_related('gcm_device').get(id = to_user_id)
        if token == from_user.token.token:
            message = Message(to_user = to_user, from_user = from_user, text = unicode(text, "utf-8"), photo = photo_file, preview = preview_file)
            message.save()
            from_user.count_outgoing_messages = F('count_outgoing_messages') + 1
            from_user.save(update_fields=['lastActivity', 'count_outgoing_messages'])
            count_incoming_messages_buf = to_user.count_incoming_messages + 1
            to_user.count_incoming_messages = F('count_incoming_messages') + 1
            to_user.save(update_fields=['count_incoming_messages'])

            # if this message is answer for another message we remove it
            if answer_for_mes_id is not None:
                try:
                    Message.objects.get(id = answer_for_mes_id).delete()
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    return HttpResponse(make_error(explanation="message with that message_id not exist", errorid="40", functionName="send_message_request"))

            # send push via Google Cloud Messages
            try:
                if to_user.gcm_device is not None:
                    to_user.gcm_device.send_message('"count_incoming_messages": "' + str(count_incoming_messages_buf) + '"')
            except Exception as e:
                return HttpResponse(make_error(explanation="some error with GCM: " + e.message, errorid="1000", functionName="send_message_request"))

            return HttpResponse('{"report" : "success", "explanation": "message has been sended", "token": "' + token_update(from_user) + '"}')
        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=from_user.id,
                                           functionName="send_message_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(make_error(explanation="user id does not exists", errorid="3", functionName="send_message_request"))


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def get_message_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()

    # Optional. Removed_message_ids that is json string. Example: '{"message_ids" : [1,2,3]}'
    remove_message_ids = None if request.POST.get("remove_message_ids") is None else request.POST.get("remove_message_ids").__str__().strip()

    if user_id is None or token is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", functionName="get_message_request"))

    try:
        user = User.objects.defer('id', 'count_incoming_messages').select_related('token').get(id = user_id)
        if token == user.token.token:
            messages = Message.objects.select_related('from_user').filter(to_user = user, is_read = '0')

            if remove_message_ids is not None:
                result = remove_messages(remove_message_ids, user)
                if result[0] is False:
                    return HttpResponse(result[1])

            messages_list = []
            for e in messages:
                messages_list.append({"from_name": e.from_user.name, "from_id": str(e.from_user.id), "datetime": str(e.send_time), "message_id": str(e.id), "from_country": e.from_user.country, "from_city": e.from_user.city, "text": e.text, "photo": e.photo.url, "preview": e.preview.url})

            # messages.update(is_read = '1')
            return HttpResponse('{"report" : "success", "explanation": "messages list has been returned", "count_incoming_messages": "' + str(user.count_incoming_messages) + '", "messages":' + json.dumps(messages_list, ensure_ascii = False) + ', "token": "' + token_update(user) + '"}')

        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="get_message_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", functionName="get_message_request"))


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def get_feed_request(request):
    sex = None if request.POST.get("sex") is None else request.POST.get("sex").__str__().strip()
    age_range = None if request.POST.get("age_range") is None else request.POST.get("age_range").__str__().strip()
    exclude_ids_as_json = None if request.POST.get("exclude_ids") is None else request.POST.get("exclude_ids").__str__().strip()

    #country = None if request.POST.get("country") is None else request.POST.get("country").__str__().strip()
    #city = None if request.POST.get("city") is None else request.POST.get("city").__str__().strip()

    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()

    if user_id is None or token is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", functionName="get_feed_request"))

    try:
        user = User.objects.select_related('token').get(id = user_id)
        if token != user.token.token:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id, functionName="get_feed_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", functionName="get_feed_request"))

    if sex is None or age_range is None or exclude_ids_as_json is None:
        return HttpResponse(make_error(explanation="missing required argument", errorid="1", functionName="get_feed_request"))

    sex = sex.upper()
    if sex != User.MALE and sex != User.FEMALE and sex != User.SEX_ANY:
        return HttpResponse(make_error(explanation="bad format in sex field", errorid="14", functionName="get_feed_request"))

    # age_range format '1' or '2' or '3'
    if age_range != User.AGE_RANGE_1 and age_range != User.AGE_RANGE_2 and age_range != User.AGE_RANGE_3 and age_range != User.AGE_RANGE_ANY:
        return HttpResponse(
            make_error(explanation="bad format in age_range field", errorid="14", functionName="get_feed_request"))

    try:
        exclude_ids_list = json.loads(exclude_ids_as_json)['user_ids']
        exclude_ids_list.append(user_id)
    except (ValueError, KeyError) as err:
        return HttpResponse(
            make_error(explanation="bad json object. in detail: " + str(err), errorid="32", functionName="get_feed_request"))

    #DEEP_SAMPLE_COUNT = 100
    COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME = 15

    # check performance when exclude before and after order_by

    #slice = randint(0, DEEP_SAMPLE_COUNT - COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME)

    if sex != User.SEX_ANY and age_range != User.AGE_RANGE_ANY:
        sample = User.objects.filter(sex = sex, age = age_range, lastActivity__gt = timezone.now() - timedelta(seconds = 3600)).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
        if len(sample) < 15:
            sample = User.objects.filter(sex = sex, age = age_range).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
            if len(sample) < 15:
                sample = User.objects.filter(sex = sex, age = age_range).exclude(id__in = [user_id]).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
    elif sex == User.SEX_ANY and age_range != User.AGE_RANGE_ANY:
        sample = User.objects.filter(age = age_range, lastActivity__gt = timezone.now() - timedelta(seconds = 3600)).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
        if len(sample) < 15:
            sample = User.objects.filter(age = age_range).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
            if len(sample) < 15:
                sample = User.objects.filter(age = age_range).exclude(id__in = [user_id]).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
    elif sex != User.SEX_ANY and age_range == User.AGE_RANGE_ANY:
        sample = User.objects.filter(sex = sex, lastActivity__gt = timezone.now() - timedelta(seconds = 3600)).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
        if len(sample) < 15:
            sample = User.objects.filter(sex = sex).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
            if len(sample) < 15:
                sample = User.objects.filter(sex = sex).exclude(id__in = [user_id]).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
    elif sex == User.SEX_ANY and age_range == User.AGE_RANGE_ANY:
        sample = User.objects.filter(lastActivity__gt = timezone.now() - timedelta(seconds = 3600)).exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
        if len(sample) < 15:
            sample = User.objects.exclude(id__in = exclude_ids_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
            if len(sample) < 15:
                sample = User.objects.order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].exclude(id__in = [user_id]).values('id', 'city', 'country', 'avatar', 'status', 'name')
    else:
        return HttpResponse(
            make_error(explanation="Sample error. Refer to Misha", errorid="21", functionName="get_feed_request"))

    # temporary block. for test.
    additional_sample = []
    if len(sample) < 15:
        exclude_list = [user_id]
        for e in sample:
            exclude_list.append(e['id'])
        additional_sample = User.objects.exclude(id__in = exclude_list).order_by('-lastActivity')[:COUNT_FEED_ENTRYS_RETURNING_AT_A_TIME].values('id', 'city', 'country', 'avatar', 'status', 'name')
    sample = list(sample) + list(additional_sample)
    # end temporary block. for test.

    for e in sample:
        e['avatar'] = settings.MEDIA_URL + e['avatar']

    # return HttpResponse(json.dumps(list(sample)))
    return HttpResponse('{"report" : "success", "explanation": "feed has been returned", "count_incoming_messages": "' + str(user.count_incoming_messages) + '", "users": '+ json.dumps(list(sample), ensure_ascii = False) +'}')


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def remove_messages_request(request):
    # example js object: '{"message_ids" : [1,2,3]}'
    message_ids_json_str = None if request.POST.get("message_ids") is None else request.POST.get("message_ids").__str__().strip()
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()

    if user_id is None or token is None or message_ids_json_str is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", userid=user_id, functionName="remove_messages_request"))

    try:
        user = User.objects.select_related('token').get(id = user_id)
        if token == user.token.token:
            result = remove_messages(message_ids_json_str, user)
            if result[0] is True:
                return HttpResponse('{"report" : "success", "explanation": "messages has been removed"}')
            else:
                return HttpResponse(result[1])
        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="remove_messages_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", userid=user_id, functionName="remove_messages_request"))


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def set_gcm_reg_id_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
    gcm_reg_id = None if request.POST.get("gcm_reg_id") is None else request.POST.get("gcm_reg_id").__str__().strip()
    device_id = None if request.POST.get("device_id") is None else request.POST.get("device_id").__str__().strip()

    if user_id is None or token is None or gcm_reg_id is None or device_id is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", userid=user_id, functionName="set_gcm_reg_id_request"))

    try:
        user = User.objects.select_related('token', 'gcm_device').get(id = user_id)
        if token == user.token.token:
            try:
                if user.gcm_device is not None:
                    if user.gcm_device.reg_id == gcm_reg_id:
                        return HttpResponse('{"report" : "success", "explanation": "reg_id is already equal to sent gcm_reg_id"}')
                    user.gcm_device.reg_id = gcm_reg_id
                    user.gcm_device.dev_id = device_id
                    user.gcm_device.save(update_fields=['reg_id', 'dev_id'])
                else:
                    gcm_device = Device.objects.create(reg_id = gcm_reg_id, name = user.email, is_active = True, dev_id = device_id)
                    user.gcm_device = gcm_device
                    user.save(update_fields=['gcm_device'])
                return HttpResponse('{"report" : "success", "explanation": "gcm device has been updated"}')
            except IntegrityError as err_obj:
                return HttpResponse(
                    make_error(explanation="IntegrityError: " + err_obj.message, errorid="39", functionName="set_gcm_reg_id_request"))
        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="set_gcm_reg_id_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", userid=user_id, functionName="set_gcm_reg_id_request"))


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def set_review_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
    # allowable values 1-5
    valuation = None if request.POST.get("valuation") is None else request.POST.get("valuation").__str__().strip()
    review_text = '' if request.POST.get("review_text") is None else request.POST.get("review_text").encode("utf-8").strip()

    if user_id is None or token is None or valuation is None or review_text is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", userid=user_id, functionName="set_review_request"))

    if valuation != Review.VALUATION_CHOICES[0][0] and valuation != Review.VALUATION_CHOICES[1][0] and valuation != \
            Review.VALUATION_CHOICES[2][0] and valuation != Review.VALUATION_CHOICES[3][0] and valuation != \
            Review.VALUATION_CHOICES[4][0]:
        return HttpResponse(make_error(explanation="bad valuation format", errorid="14", userid=user_id, functionName="set_review_request"))

    try:
        user = User.objects.select_related('token').get(id = user_id)
        if token == user.token.token:
            Review.objects.create(valuation = valuation, review_text = review_text, from_user = user)
            return HttpResponse('{"report" : "success", "explanation": "review sent"}')
        else:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="set_review_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user id does not exists", errorid="3", userid=user_id, functionName="set_review_request"))