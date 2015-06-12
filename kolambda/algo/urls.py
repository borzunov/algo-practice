from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check/random/$', views.check_random, name='check_random'),
    url(r'^check/(?P<algorithm_slug>[\w-]+)/$', views.check, name='check'),
    url(r'^submit/(?P<algorithm_slug>[\w-]+)/$',
        views.create_submit, name='create_submit'),
    url(r'^history/(?P<author_username>[\w-]+)/$',
        views.history, name='history'),
    url(r'^history/(?P<author_username>[\w-]+)/(?P<algorithm_slug>[\w-]+)/$',
        views.history, name='history'),
    url(r'^history/(?P<author_username>[\w-]+)/(?P<algorithm_slug>[\w-]+)/' +
        r'(?P<submit_id>\d+)/$',
        views.show_submit, name='show_submit'),
    url(r'^history/(?P<author_username>[\w-]+)/(?P<algorithm_slug>[\w-]+)/' +
        r'(?P<submit_id>\d+)/new/$',
        views.show_submit, {'new_submit': True}, name='show_new_submit'),
]
