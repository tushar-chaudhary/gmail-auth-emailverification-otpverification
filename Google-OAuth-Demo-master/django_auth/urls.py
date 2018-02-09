from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views
from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup/$', signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),  # <- Here
    url(r'^$', home, name='home'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    url(r'^sms/$', index, name="index"),
    url(r'^verify/$', verify, name="verify"),
    url(r'^checkCode/$', checkCode, name="checkCode")
]
