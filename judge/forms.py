from django import forms
from judge.models import Coder, Problem, TestCase
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = {'username', 'password'}

