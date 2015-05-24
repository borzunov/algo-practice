from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check/random/$', views.check,
        {'algorithm_random': True}, name='check_random'),
    url(r'^check/(?P<algorithm_slug>[\w-]+)/$', views.check, name='check'),
    url(r'^submit/(?P<algorithm_slug>[\w-]+)/$', views.submit, name='submit'),
    url(r'^history/(?P<author_username>[\w-]+)/$',
        views.history, name='history'),
    url(r'^history/(?P<author_username>[\w-]+)/(?P<algorithm_slug>[\w-]+)/$',
        views.history, name='history'),
]
