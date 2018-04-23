from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Question, Choice, Votes, Survey

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login, authenticate,logout

from django.contrib.auth.decorators import login_required

from .forms import UserLoginForm, PollForm, PollChoiceForm, SurveyForm, SignupForm

from django.contrib.auth.models import User

from django.urls import reverse

import requests

from django.conf import settings

from django.contrib import messages

from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import get_current_site

from django.utils.encoding import force_bytes, force_text

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token

from django.core.mail import EmailMessage

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
        form = SignupForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('polls/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token':account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
                return HttpResponse('Please confirm your email address to complete the registration')
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
    else:
        form = SignupForm()

    context = { 'form' : form }
    return render(request, 'polls/register.html', context)

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('polls:dashboard')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

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
@login_required(login_url='/login')
def mypolls(request):
    username = request.user
    latest_question_list = Question.objects.filter(username = username)
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/mypolls.html',context)

@login_required(login_url='/login')
def mysurvey(request):
    username = request.user
    survey_list = Survey.objects.filter(username=username)
    context = {
        'survey_list': survey_list,
    }
    return render(request, 'polls/mysurvey.html',context)




    
@login_required(login_url='/login')
def createsurvey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            username = request.user
            survey = username.survey_set.create(title=request.POST['title'],modified=request.POST['modified'])
            username.survey_set.update(responses =0)
            return redirect('polls:mysurvey')
    else:
        form = SurveyForm()
    username = request.user
    survey_list = Survey.objects.filter(username=username)
    context = {'form':form, 'survey_list':survey_list}
    return render(request,'polls/createsurvey.html', context)

@login_required(login_url='/login')
def editsurvey(request,survey_id):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = get_object_or_404(Survey,pk=survey_id)
            survey.title = request.POST['title']
            survey.modified = request.POST['modified']
            survey.save()
            # question.survey_set.update(votes =0)
            return redirect('polls:mysurvey')
    else:
        survey = get_object_or_404(Survey,pk=survey_id)
        data={'title' : survey.title,'modified' : survey.modified}
        form = SurveyForm(data)

    context = { 'form' : form, 'survey' : survey }
    return render(request,'polls/editsurvey.html', context)

@login_required(login_url='/login')
def deletesurvey(request,survey_id):
    question = get_object_or_404(Survey,pk=survey_id)
    question.delete()
    return redirect('polls:mysurvey')   

@login_required(login_url='/login')
def createpolls(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            username = request.user
            question = username.question_set.create(question_text=request.POST['question_text'],pub_date=request.POST['pub_date'])
            return redirect('polls:mypolls')
    else:
        form = PollForm()
    username = request.user
    latest_question_list = Question.objects.filter(username = username)
    context = { 'form' : form,'latest_question_list': latest_question_list }
    return render(request,'polls/createpolls.html', context)


@login_required(login_url='/login')
def createchoice(request,question_id):
    if request.method == 'POST':
        form = PollChoiceForm(request.POST)
        if form.is_valid():
            question = get_object_or_404(Question, pk=question_id)
            choice = question.choice_set.create(choice_text=request.POST['choice_text'])
            question.choice_set.update(votes =0)
            vote = Votes.objects.filter(question_text= question.question_text)
            vote.delete()
            return redirect('polls:mypolls')
    else:
        form = PollChoiceForm()
    question = get_object_or_404(Question, pk=question_id)
    context = { 'form' : form,'question' : question}
    return render(request,'polls/createchoice.html', context)

@login_required(login_url='/login')
def editpoll(request,question_id):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            question = get_object_or_404(Question,pk=question_id)
            question.question_text = request.POST['question_text']
            question.pub_date = request.POST['pub_date']
            question.save()
            question.choice_set.update(votes =0)
            vote = Votes.objects.filter(question_text= question.question_text)
            vote.delete()
            return redirect('polls:mypolls')
    else:
        question = get_object_or_404(Question,pk=question_id)
        data={'question_text' : question.question_text,'pub_date' : question.pub_date}
        form = PollForm(data)

    context = { 'form' : form, 'question' : question }
    return render(request,'polls/editpoll.html', context)

@login_required(login_url='/login')
def editchoice(request,choice_id):
    if request.method == 'POST':
        form = PollChoiceForm(request.POST)
        if form.is_valid():
            choice = get_object_or_404(Choice,pk=choice_id)
            choice.choice_text = request.POST['choice_text']
            choice.votes = 0
            choice.save()
            question = choice.question
            question.choice_set.update(votes =0)
            vote = Votes.objects.filter(question_text= question)
            vote.delete()
            return redirect('polls:mypolls')
    else:
        choice = get_object_or_404(Choice,pk=choice_id)
        data={'choice_text' : choice.choice_text}
        form = PollChoiceForm(data)
    
    context = { 'form' : form, 'choice' : choice }
    return render(request,'polls/editchoice.html', context)

@login_required(login_url='/login')
def deletepoll(request,question_id):
     question = get_object_or_404(Question,pk=question_id)
     question.delete()
     vote = Votes.objects.filter(question_text= question.question_text)
     vote.delete()
     return redirect('polls:mypolls')

@login_required(login_url='/login')
def deletechoice(request,choice_id):
     choice = get_object_or_404(Choice,pk=choice_id)
     choice.delete()
     vote = Votes.objects.filter(question_text= choice.question)
     vote.delete()
     return redirect('polls:mypolls')

@login_required(login_url='/login')
def chart(request,question_id):
    return render(request,'polls/chart.html',{"question_id" : question_id})

@login_required(login_url='/login')
def chartdata(request,question_id):
    votes=[]
    ch=[]
    question = get_object_or_404(Question,pk=question_id)
    choices = question.choice_set.all()
    for choice in choices:
        ch.append(choice.choice_text)
        votes.append(choice.votes)
    qs_count = User.objects.all().count()
    labels = ch
    default_items = votes
    data={
        "labels" : labels,
        "default" : default_items,
    }
    return JsonResponse(data)
