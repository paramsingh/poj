from django.conf.urls import patterns, url
from judge import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register_user, name='register'),
        url(r'^logout/$', views.loguserout, name = 'loguserout'),
        url(r'^login/$', views.loguserin, name = 'loguserin'),
        url(r'^add-problem/$', views.add_problem, name = "add_problem"),
        url(r'^problems/$', views.all_problems, name = "all_problems"),
        url(r'^problems/(?P<pid>[\w\-]+)$', views.view_problem, name="view_prob"),
        url(r'^submit/(?P<pid>[\w\-]+)$', views.submit, name="submit"),
        url(r'^submission/(?P<submission_id>[\d]+)$', views.view_submission, name="view_sub"),
]
