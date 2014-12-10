from django.shortcuts import render
from django.http import HttpResponse
from requests import HTTPError
from Server.models import User
from tools import make_error
import random, json

__author__ = 'Mihail'

from django.views.decorators.csrf import csrf_exempt

#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def get_gcm_control_panel(request):
    themes = None if request.POST.getlist("theme[]").__len__() == 0 else request.POST.getlist("theme[]")
    texts = None if request.POST.getlist("text[]").__len__() == 0 else request.POST.getlist("text[]")
    locales = None if request.POST.getlist("locale[]").__len__() == 0 else request.POST.getlist("locale[]")
    notification_type_code = None if request.POST.get("notification_type_code") is None else request.POST.get("notification_type_code").__str__().strip()
    link = None if request.POST.get("link") is None else request.POST.get("link").__str__().strip()
    app_version = None if request.POST.get("app_version") is None else request.POST.get("app_version").__str__().strip()

    if themes is None or texts is None or locales is None:
        return render(request, 'gcm_control_panel.html')

    russian_locales = ['ru', 'et', 'lv', 'uk', 'bg', 'kk', 'ro', 'sr', 'sk', 'sl', 'uz', 'tk', 'ka', 'hy', 'az', 'be']
    messages = {}
# unicode(text, "utf-8")
    i = 0
    while len(themes) > i:
        if len(texts[i]) > 0 and len(themes[i]) > 0 and len(locales[i]) > 0:
            messages[locales[i]] = json.dumps({"theme": themes[i].encode("utf-8").strip(), "text": texts[i].encode("utf-8").strip(), "notification_type_code": notification_type_code, "link": str(link), "app_version": str(app_version)}, ensure_ascii = False)
        i += 1

    users = User.objects.all().select_related('gcm_device')

    random_lacale = random.sample(messages.values(), 1)

    def send_gcm_message(user, message):
        if user.gcm_device is None:
            return False, "user.gcm_device is None. (user_id: " + str(user.id) + ")"
        try:
            user.gcm_device.send_message(message)
            return True, "success"
        except HTTPError as errObj:
            return False, errObj.message + " (user_id: " + str(user.id) + ")"

    errors = []

    for user in users:
        if user.gcm_device is None:
            continue
        if user.locale in russian_locales and "ru" in messages:
            result = send_gcm_message(user, messages["ru"])
            if result[0] is False:
                errors.append(result[1])
            continue
        elif user.locale in messages:
            result = send_gcm_message(user, str(messages[user.locale]))
            if result[0] is False:
                errors.append(result[1])
            continue
        elif "en" in messages:
            result = send_gcm_message(user, str(messages["en"]))
            if result[0] is False:
                errors.append(result[1])
            continue
        else:
            result = send_gcm_message(user, str(random_lacale))
            if result[0] is False:
                errors.append(result[1])
            continue

    if len(errors) != 0:
        html_table = '<table border="1">'
        for e in errors:
            html_table += '<tr><td>' + e + '</td></tr>'
        html_table += '</table>'
    else:
        html_table = ""
    return HttpResponse('{"report" : "success", "explanation": "push notices were sent", "errors": "' + html_table + '"}')

    # context = {}
    # return render(request, 'gcm_control_panel.html', context)


#@ratelimit(block=True, rate='10/m')
@csrf_exempt
def verification_avatars_panel(request):
    denial_user_ids = None if request.POST.getlist("denial_user_ids[]").__len__() == 0 else request.POST.getlist("denial_user_ids[]")
    confirmation_user_ids = None if request.POST.getlist("confirmation_user_ids[]").__len__() == 0 else request.POST.getlist("confirmation_user_ids[]")
    banned_user_ids = None if request.POST.getlist("banned_user_ids[]").__len__() == 0 else request.POST.getlist("banned_user_ids[]")

    if denial_user_ids is not None and len(denial_user_ids) > 0:
        User.objects.filter(id__in = denial_user_ids).update(user_state = User.TYPE_OF_USER_STATE[3][0])

    if confirmation_user_ids is not None and len(confirmation_user_ids) > 0:
        User.objects.filter(id__in = confirmation_user_ids).update(user_state = User.TYPE_OF_USER_STATE[0][0])

    if banned_user_ids is not None and len(banned_user_ids) > 0:
        User.objects.filter(id__in = banned_user_ids).update(user_state = User.TYPE_OF_USER_STATE[1][0])

    DEEP_SAMPLE_USERS_COUNT = 10
    users = User.objects.filter(user_state = User.TYPE_OF_USER_STATE[2][0])[:DEEP_SAMPLE_USERS_COUNT]
    context = {"users": users}
    return render(request, 'avatar_check_console.html', context)