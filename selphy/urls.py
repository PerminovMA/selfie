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
    url(r'^add_user_request/$', 'Server.views.views.add_user_request'),
    url(r'^check_email_exists/$', 'Server.views.views.check_email_exists_request'),
    url(r'^change_avatar_request/$', 'Server.views.views_change.change_avatar_request'),
    url(r'^send_message_request/$', 'Server.views.views.send_message_request'),
    url(r'^get_message_request/$', 'Server.views.views.get_message_request'),
    url(r'^get_feed_request/$', 'Server.views.views.get_feed_request'),
    url(r'^remove_messages_request/$', 'Server.views.views.remove_messages_request'),
    url(r'^set_gcm_reg_id_request/$', 'Server.views.views.set_gcm_reg_id_request'),
    url(r'^set_review_request/$', 'Server.views.views.set_review_request'),
    url(r'^get_fake_message_request/$', 'Server.views.views.get_fake_message_request'),
    url(r'^change_location_request/$', 'Server.views.views_change.change_location_request'), # deprecated 06.12.14
    url(r'^change_gcm_request/$', 'Server.views.views_change.change_gcm_request'), # deprecated 06.12.14
    url(r'^gcm_control_panel/$', 'Server.views.views_control_panel.get_gcm_control_panel'),
    url(r'^verification_avatars_panel/$', 'Server.views.views_control_panel.verification_avatars_panel'),
    url(r'^change_user_info_request/$', 'Server.views.views_change.change_user_info_request'),
    url(r'^send_feedback_request/$', 'Server.views.views.send_feedback_request'),
    url(r'^add_bookmark_request/$', 'Server.views.views_bookmark.add_bookmark_request'),
    url(r'^get_bookmarks_request/$', 'Server.views.views_bookmark.get_bookmarks_request'),
    # url(r'^remove_bookmark_request/$', 'Server.views.views_bookmark.remove_bookmark_request'),
)
