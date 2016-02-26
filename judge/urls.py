from django.conf.urls import patterns, url
from judge import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register_user, name='register'),
        ]
