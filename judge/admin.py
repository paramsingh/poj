from django.contrib import admin
from judge.models import Problem, Coder, Submission, TestCase
from judge.models import UnevaluatedSubmission

admin.site.register(Problem)
admin.site.register(Coder)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(UnevaluatedSubmission)

