from django.db import models
from random import randint
from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver
from gcm.models import Device
from Server.properties import COUNT_FOLDERS
from time import time


class Token(models.Model):
    token = models.CharField(max_length=50)
    produce = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.token


def generate_filename(filename):
    """returns the new name for save on the server"""
    return str(time()).replace('.', '_') + str(randint(0, 100000)) + filename[filename.rfind('.'):]


def get_upload_avatar_filename(instance, filename):
    return "avatars/%s/%s/" % (str(randint(1, COUNT_FOLDERS)), str(randint(1, COUNT_FOLDERS))) + generate_filename(filename)


def get_upload_photo_filename(instance, filename):
    return "photos/%s/%s/" % (str(randint(1, COUNT_FOLDERS)), str(randint(1, COUNT_FOLDERS))) + generate_filename(filename)


def get_upload_preview_filename(instance, filename):
    return "previews/%s/%s/" % (str(randint(1, COUNT_FOLDERS)), str(randint(1, COUNT_FOLDERS))) + generate_filename(filename)


class User(models.Model):
    AGE_RANGE_1 = '1'
    AGE_RANGE_2 = '2'
    AGE_RANGE_3 = '3'
    AGE_RANGE_ANY = 'ANY'
    MALE = 'M'
    FEMALE = 'F'
    SEX_ANY = 'ANY'

    TYPE_OF_AGE = (
        (AGE_RANGE_1, '13-17'),
        (AGE_RANGE_2, '18-39'),
        (AGE_RANGE_3, '40+'),
    )

    TYPE_OF_SEX = (
        (MALE, 'male'),
        (FEMALE, 'female'),
    )

    name = models.CharField(max_length=25, null=False, blank=False)
    email = models.EmailField(db_index=True, null=False, blank=False, unique=True)
    age = models.CharField(choices=TYPE_OF_AGE, max_length=1, null=False, blank=False, db_index=True)  # "1" or "2" or "3"
    sex = models.CharField(choices=TYPE_OF_SEX, max_length=1, null=False, blank=False, db_index=True)  # "M" or "F"
    regDate = models.DateField(auto_now_add=True)
    lastActivity = models.DateTimeField(auto_now=True, db_index=True)
    avatar = models.FileField(upload_to=get_upload_avatar_filename, null=True, blank=True)
    status = models.CharField(max_length=140, null=False, blank=True)
    token = models.ForeignKey(Token)
    city = models.CharField(max_length=50, null=True, blank=False)
    country = models.CharField(max_length=50, null=True, blank=False)
    gcm_device = models.ForeignKey(Device, null=True, blank=True)  # google cloud messages obj (django_gcm module) for send push messages
    count_incoming_messages = models.PositiveIntegerField(default=0)  # total count incoming messages
    count_outgoing_messages = models.PositiveIntegerField(default=0)  # total count outgoing messages

    def __unicode__(self):
        return self.email


@receiver(pre_delete, sender=User)
def user_avatar_deleter(sender, instance, **kwargs):
    if not instance.avatar.name:
        return

    if instance.avatar is not None:
        instance.avatar.delete(False)

@receiver(post_delete, sender=User)
def user_gcm_device_deleter(sender, instance, **kwargs):
    if instance.gcm_device is not None:
        instance.gcm_device.delete()


class Message(models.Model):
    TYPE_OF_READ = (
        ('1', 'read'),
        ('0', 'unread'),
    )

    to_user = models.ForeignKey('User', db_index=True, related_name="incoming_message_set")
    from_user = models.ForeignKey('User', related_name="outgoing_message_set")
    text = models.CharField(max_length=140, null=False, blank=True)
    photo = models.FileField(upload_to=get_upload_photo_filename, null=False, blank=False)
    preview = models.FileField(upload_to=get_upload_preview_filename, null=False, blank=False)
    is_read = models.CharField(choices=TYPE_OF_READ, max_length=1, null=False, blank=False, db_index=True, default='0') # '1' or '0'
    send_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.to_user)


@receiver(pre_delete, sender=Message)
def message_photo_deleter(sender, instance, **kwargs):
    if not instance.photo.name:
        return

    if instance.photo is not None:
        instance.photo.delete(False)


class Error(models.Model):
    explanation = models.CharField(max_length = 100, null = True, blank = True)
    errorid = models.CharField(max_length = 10, null = True, blank = True)
    user = models.ForeignKey(User, null = True, blank = True)
    functionName = models.CharField(max_length = 100, null = True, blank = True)
    errorDateTime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.explanation)


class Review(models.Model):
    VALUATION_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))

    valuation = models.CharField(choices=VALUATION_CHOICES, max_length=1, null=False, blank=False)
    review_text = models.CharField(max_length=150, null=False, blank=True)
    from_user = models.ForeignKey(User)

    def __unicode__(self):
        return str(self.valuation)