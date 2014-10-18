__author__ = 'Mihail'
from django.contrib import admin
import Server.models


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'token', 'lastActivity', 'regDate', 'city', 'country')
    search_fields = ['email']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'to_user', 'from_user', 'is_read')
    search_fields = ['text']


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('errorid', 'explanation', 'user', 'functionName', 'errorDateTime')


class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'produce')


admin.site.register(Server.models.User, UserAdmin)
admin.site.register(Server.models.Token, TokenAdmin)
admin.site.register(Server.models.Error, ErrorAdmin)
admin.site.register(Server.models.Message, MessageAdmin)
admin.site.register(Server.models.Review)