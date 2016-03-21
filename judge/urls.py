from django.conf.urls import patterns, url
from judge import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register_user, name='register'),
        url(r'^logout/$', views.loguserout, name = 'loguserout'),
        url(r'^login/$', views.loguserin, name = 'loguserin'),
        url(r'^add-problem/$', views.add_problem, name = "add_problem"),
]
