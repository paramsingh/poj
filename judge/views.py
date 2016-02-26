from django.shortcuts import render
from django.http import HttpResponse
from judge.models import Problem, Submission, Coder, TestCase
from judge.forms import UserForm


def index(request):
    return HttpResponse("Hello, world!")


def register_user(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            # save the user to the db
            u = user_form.save()
            u.set_password(u.password)
            u.save()

            coder = Coder(user = u)
            coder.link = "/judge/users/%s" % (u.username)
            coder.score = 0
            coder.rank = len(Coder.objects.all()) + 1
            coder.save()
            registered = True
        else:
            print user_form.errors
    else:
        user_form = UserForm()
    return render(request, "judge/register.html", {"user_form": user_form, "registered": registered})

