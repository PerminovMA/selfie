from Server.models import Error, User, Token
from django.core.exceptions import ObjectDoesNotExist
import random, string
from django.utils import timezone
from datetime import timedelta
from properties import TOKEN_LEN, TOKEN_UPDATE_INTERVAL
import json
__author__ = 'Mihail'


def check_if_email_exists(email):
    return User.objects.filter(email=email).count() > 0


def make_error(explanation, errorid, userid = None, functionName = None):
    if userid is None:
        err = Error(explanation = str(explanation), errorid = str(errorid), functionName = functionName)
        err.save()
    else:
        try:
            userid = int(userid)
        except ValueError:
            err = Error(explanation = "userid " + str(userid) + " is not int (" + str(functionName) + ")", errorid = "10", functionName = "make_error")
            err.save()
            return '{"report" : "error", "explanation": "userid is not int", "errorid": "10"}'
        try:
            u = User.objects.get(id = userid)
            err = Error(explanation = str(explanation), errorid = str(errorid), functionName = functionName, user = u)
            err.save()
        except ObjectDoesNotExist:
            err = Error(explanation = "user with that userid " + str(userid) + " does not exists (" + str(functionName) + ")", errorid = "6", functionName = "make_error")
            err.save()
            return '{"report" : "error", "explanation": "user with that userid has not exists", "errorid": "6"}'

    return '{"report" : "error", "explanation": "' + str(explanation) + '", "errorid": "' + str(errorid) + '"}'


def random_str(count_chars=TOKEN_LEN):
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in xrange(count_chars))


def get_new_token():
    token = Token(token=random_str())
    token.save()
    return token


def token_update(user):
    if timezone.now() - user.token.produce > timedelta(seconds = TOKEN_UPDATE_INTERVAL):
        user.token.token = random_str()
        user.token.save()
    return user.token.token


def remove_messages(json_with_mes_ids_str, user_obj):
    """
        Deletes messages. id messages are described in the 'json_with_mes_ids_str' argument
        example json_with_mes_ids_str: '{"message_ids" : [1, 2, 3]}'
    """
    try:
        message_ids_json_obj = json.loads(json_with_mes_ids_str)
    except (ValueError, KeyError) as err:
        return (False, make_error(explanation="bad json object. in detail: " + str(err), errorid="32",
                                  functionName="remove_messages"))

    try:
        user_obj.incoming_message_set.filter(id__in=message_ids_json_obj["message_ids"]).delete()
        return (True, None)
    except ValueError:
        return (False, make_error(explanation="Bad message_ids (perhsaps, not int)", errorid="32",
                                  functionName="remove_messages"))