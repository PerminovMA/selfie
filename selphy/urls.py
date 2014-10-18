from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from settings import MEDIA_ROOT
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('gcm.urls')),
    url(r'^photos/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + 'photos/'}),
    url(r'^avatars/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + 'avatars/'}),
    url(r'^previews/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + 'previews/'}),
    # Examples:
    # url(r'^$', 'selphy.views.home', name='home'),
    # url(r'^selphy/', include('selphy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add_user_request/$', 'Server.views.add_user_request'),
    url(r'^check_email_exists/$', 'Server.views.check_email_exists_request'),
    url(r'^change_avatar_request/$', 'Server.views.change_avatar_request'),
    url(r'^send_message_request/$', 'Server.views.send_message_request'),
    url(r'^get_message_request/$', 'Server.views.get_message_request'),
    url(r'^get_feed_request/$', 'Server.views.get_feed_request'),
    url(r'^remove_messages_request/$', 'Server.views.remove_messages_request'),
    url(r'^set_gcm_reg_id_request/$', 'Server.views.set_gcm_reg_id_request'),
    url(r'^set_review_request/$', 'Server.views.set_review_request'),
)
