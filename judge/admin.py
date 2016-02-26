from django.contrib import admin
from judge.models import Problem, Coder, Submission, TestCase

admin.site.register(Problem)
admin.site.register(Coder)
admin.site.register(Submission)
admin.site.register(TestCase)

