from django.conf.urls import patterns, url
from judge import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'))
