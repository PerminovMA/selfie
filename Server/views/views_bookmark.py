__author__ = 'Mihail'

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from Server.tools import make_error
from Server.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
from selphy.settings import MEDIA_URL


# @ratelimit(block=True, rate='10/m')
@csrf_exempt
def add_bookmark_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get(
        "user_id").__str__().strip()
    to_user_id = None if request.POST.get("to_user_id") is None else request.POST.get("to_user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()

    if user_id is None or token is None or to_user_id is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", userid=user_id,
                       functionName="add_bookmark_request"))

    try:
        from_user = User.objects.select_related('token').get(id=user_id)
        to_user = User.objects.get(id=to_user_id)
        if token != from_user.token.token:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=from_user.id,
                                           functionName="add_bookmark_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user with from_user_id or to_user_id does not exists", errorid="3",
                       functionName="add_bookmark_request"))

    from_user.bookmarks.add(to_user)

    return HttpResponse('{"report" : "success", "explanation": "Bookmark added"}')


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def get_bookmarks_request(request):
    user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
    token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()

    # optional. Users with id in user_ids_json_str will be removed from bookmark
    # example js object: '{"user_ids" : [1, 2, 3]}'
    user_ids_json_str = None if request.POST.get("user_ids") is None or request.POST.get("user_ids") == '' else request.POST.get("user_ids").__str__().strip()

    if user_id is None or token is None:
        return HttpResponse(
            make_error(explanation="missing required argument", errorid="1", userid=user_id,
                       functionName="get_bookmark_request"))

    try:
        user = User.objects.select_related('token').get(id=user_id)
        if token != user.token.token:
            return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
                                           functionName="get_bookmark_request"))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse(
            make_error(explanation="user with from_user_id or to_user_id does not exists", errorid="3",
                       functionName="get_bookmark_request"))

    if user_ids_json_str is not None:
        try:
            user_ids_json_obj = json.loads(user_ids_json_str)
            user.bookmarks.remove(*user_ids_json_obj['user_ids'])
        except (ValueError, KeyError) as err:
            return HttpResponse(make_error(explanation="bad json object. in detail: " + err.message, errorid="32", functionName="get_bookmarks_request"))

    bookmarks = user.bookmarks.values('id', 'avatar', 'name', 'country', 'city', 'avatar_preview')
    for e in bookmarks:
        if e['avatar'] != '':
            e['avatar'] = MEDIA_URL + e['avatar']
        if e['avatar_preview'] != '' and e['avatar_preview'] is not None:
            e['avatar_preview'] = MEDIA_URL + e['avatar_preview']
        else:
            e['avatar_preview'] = ''

    return HttpResponse(
        '{"report" : "success", "explanation": "Bookmarks returned", "bookmarks": ' + json.dumps(list(bookmarks),
        ensure_ascii=False) + '}')


# @ratelimit(block=True, rate='10/m')
# @csrf_exempt
# def remove_bookmark_request(request):
#     user_id = None if request.POST.get("user_id") is None else request.POST.get("user_id").__str__().strip()
#     token = None if request.POST.get("token") is None else request.POST.get("token").__str__().strip()
#     # example js object: '{"user_ids" : [1, 2, 3]}'
#     user_ids_json_str = None if request.POST.get("user_ids") is None else request.POST.get("user_ids").__str__().strip()
#
#     if user_id is None or token is None or user_ids_json_str is None:
#         return HttpResponse(
#             make_error(explanation="missing required argument", errorid="1", userid=user_id,
#                        functionName="remove_bookmark_request"))
#
#     try:
#         user = User.objects.select_related('token').get(id=user_id)
#         # remove_user = User.objects.get(id=remove_user_id)
#         if token != user.token.token:
#             return HttpResponse(make_error(explanation="token is poor", errorid="100", userid=user.id,
#                                            functionName="remove_bookmark_request"))
#     except (ObjectDoesNotExist, MultipleObjectsReturned):
#         return HttpResponse(
#             make_error(explanation="user with from_user_id or to_user_id does not exists", errorid="3",
#                        functionName="remove_bookmark_request"))
#
#     try:
#         user_ids_json_obj = json.loads(user_ids_json_str)
#         user.bookmarks.remove(*user_ids_json_obj['user_ids'])
#     except (ValueError, KeyError) as err:
#         return HttpResponse(make_error(explanation="bad json object. in detail: " + err.message, errorid="32", functionName="remove_bookmark_request"))
#
#     return HttpResponse('{"report" : "success", "explanation": "Bookmark removed"}')