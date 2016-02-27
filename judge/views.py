from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from judge.models import Problem, Submission, Coder, TestCase
from judge.forms import UserForm


def index(request):
    return render(request, "judge/index.html")


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
            # calculation of rank in the beginning
            coder.rank = -1
            for k in Coder.objects.all():
                coder.rank = max(coder.rank, k.rank)
            coder.save()
            registered = True
        else:
            print user_form.errors
    else:
        user_form = UserForm()
    return render(request, "judge/register.html", {"user_form": user_form, "registered": registered})


def loguserin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect('/judge/')
        else:
            print "Invalid login details: {}, {}".format(username, password)
            return HttpResponse("Invalid Login Details")
    else:
        return render(request, "judge/login.html", {})

def loguserout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect("/judge/")

