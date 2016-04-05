from django import forms
from judge.models import Coder, Problem, TestCase, Submission
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = {'username', 'password'}

class ProblemForm(forms.ModelForm):
    name = forms.CharField()
    code = forms.CharField()
    statement = forms.CharField(widget = forms.Textarea)
    time_limit = forms.IntegerField()
    source = forms.CharField()
    input1 = forms.FileField()
    output1 = forms.FileField()

    class Meta:
        model = Problem
        fields = ['name', 'code', 'statement', 'time_limit', 'source', 'input1', 'output1']


class SubmissionForm(forms.ModelForm):
    langs = [("C", "C"),  ("CPP", "C++"), ("JAVA", "Java"), ("PYTH", "python"), ("PYTH3", "python 3")]
    lang = forms.ChoiceField(choices = langs)
    code = forms.CharField(widget = forms.Textarea)

    class Meta:
        model = Submission
        fields = ['lang', 'code']
