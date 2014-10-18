"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
import json
from Server.models import User, Token
client = Client()


def create_user(name = "Some_Name", email = 'Perminov777@mail.ru', sex = User.MALE, age = User.MALE, token = None):
    if token is None:
        token = Token.objects.create(token = 'some_token')
    return User.objects.create(name = name, email = email, sex = sex, age = age, token = token)


class TestCheckEmailExistsRequest(TestCase):

    def test_check_email_exists_request_witout_parameters(self):
        json_responce = client.post('/check_email_exists/').content
        responce = json.loads(json_responce)
        self.assertEqual((responce["report"], responce["errorid"]), ("error", "1"))

    def test_check_email_exists_request_without_appropriate_user(self):
        json_responce = client.post('/check_email_exists/', {'email': 'Perminov777@mail.ru'}).content
        responce = json.loads(json_responce)
        report = responce["report"]
        is_match = responce["match"]
        self.assertEqual((report, is_match), ("success", "false"))

    def test_check_email_exists_request_with_appropriate_user(self):
        create_user()
        json_responce = client.post('/check_email_exists/', {'email': 'Perminov777@mail.ru'}).content
        responce = json.loads(json_responce)
        report = responce["report"]
        is_match = responce["match"]
        self.assertEqual((report, is_match), ("success", "true"))


class TestAddUserRequest(TestCase):

    def test_add_user_request_witout_parameters(self):
        json_responce = client.post('/add_user/').content
        responce = json.loads(json_responce)
        self.assertEqual((responce["report"], responce["errorid"]), ("error", "1"))

    def test_add_user_request_with_wrong_name_parameter(self):
        SHORT_NAME = ''
        LONG_NAME = 'ersdkl;kjhgfdsafghjkl;jhgfdsafghjkl;jhgfdzsxcvbnm,'

        json_responce = client.post('/add_user/', {'email': 'Perminov777@mail.ru', 'sex': User.MALE, 'age_range': User.AGE_RANGE_2, 'name': SHORT_NAME}).content
        responce = json.loads(json_responce)
        report_for_short_name = responce["report"]
        error_id_for_short_name = responce["errorid"]

        json_responce = client.post('/add_user/', {'email': 'Perminov777@mail.ru', 'sex': User.MALE, 'age_range': User.AGE_RANGE_2, 'name': LONG_NAME}).content
        responce = json.loads(json_responce)
        report_for_long_name = responce["report"]
        error_id_for_long_name = responce["errorid"]

        self.assertEqual((report_for_short_name, error_id_for_short_name), ("error", "37"))
        self.assertEqual((report_for_long_name, error_id_for_long_name), ("error", "37"))

    def test_add_user_request_with_wrong_sex_parameter(self):
        SEX = 'MALE' # must be 'M' or 'F'

        json_responce = client.post('/add_user/', {'email': 'Perminov777@mail.ru', 'sex': SEX, 'age_range': User.AGE_RANGE_2, 'name': 'some_name'}).content
        responce = json.loads(json_responce)
        self.assertEqual((responce["report"], responce["errorid"]), ('error','14'))

    def test_add_user_request_with_wrong_age_range_parameter(self):
        AGE_RANGE = '50' # must be User.AGE_RANGE_1 or User.AGE_RANGE_2 or User.AGE_RANGE_3

        json_responce = client.post('/add_user/', {'email': 'Perminov777@mail.ru', 'sex': User.MALE, 'age_range': AGE_RANGE, 'name': 'some_name'}).content
        responce = json.loads(json_responce)
        self.assertEqual((responce["report"], responce["errorid"]), ('error', '14'))

    def test_add_user_request_with_exist_email(self):
        EMAIL = 'Perminov777@mail.ru'
        create_user(email=EMAIL)

        json_responce = client.post('/add_user/', {'email': EMAIL, 'sex': User.MALE, 'age_range': User.AGE_RANGE_2, 'name': 'some_name'}).content
        responce = json.loads(json_responce)
        self.assertEqual((responce["report"], responce["errorid"]), ('error', '15'))