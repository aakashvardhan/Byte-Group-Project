from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Question, Choice, Votes

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login, authenticate,logout

from django.contrib.auth.decorators import login_required

from .forms import UserLoginForm

from django.contrib.auth.models import User

from django.urls import reverse

import requests

from django.conf import settings

from django.contrib import messages

def home(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    return render(request, 'polls/home.html')


def log_in(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('polls:dashboard')
            else:
                return render(request,'polls/login.html',{'form' : form,'user' : user})
    else:
        form = UserLoginForm
    context = { 'form' : form }
    return render(request,'polls/login.html', context)


def log_out(request):
    logout(request)
    return redirect('polls:home')



def register(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
                form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('polls:dashboard')
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
    else:
        form = UserCreationForm()

    context = { 'form' : form }
    return render(request, 'polls/register.html', context)

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

@login_required(login_url='/login')
def dashboard(request):
    username = request.user
    latest_question_list = Question.objects.exclude(username = username)
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/dashboard.html',context)

def vote(request,question_id):
    username = request.user
    latest_question_list = Question.objects.exclude(username = username)
    question = get_object_or_404(Question, pk=question_id)
    try:
        voted_question = Votes.objects.get(username = username,question_text = question)
    except Votes.DoesNotExist:
        voted_question = None
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/dashboard.html', {
            'latest_question_list': latest_question_list,
            'error_message': "You didn't select a choice.",
        })
    else:
        if voted_question == None: 
            selected_choice.votes += 1
            selected_choice.save()
            u = Votes(username = username,question_text = question)
            u.save()
            return render(request, 'polls/vote.html',{'choice' : selected_choice})
        else:
            return render(request, 'polls/dashboard.html', {
                'latest_question_list': latest_question_list,
                'error_message': "You cant vote twice",
                })

def mypolls(request):
    username = request.user
    latest_question_list = Question.objects.filter(username = username)
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/mypolls.html',context)