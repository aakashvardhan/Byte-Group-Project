from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Question, Choice, Votes, Surveytitle, Surveyquestion, Surveyanswer

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login, authenticate,logout

from django.contrib.auth.decorators import login_required

from .forms import UserLoginForm, PollForm, PollChoiceForm, SurveyForm, SignupForm,SurveyResponseForm

from django.contrib.auth.models import User

from django.urls import reverse

from django.forms import formset_factory,BaseFormSet

import requests

from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.forms import PasswordChangeForm

from django.conf import settings

from django.contrib import messages

from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import get_current_site

from django.utils.encoding import force_bytes, force_text

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token

from django.core.mail import EmailMessage

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    return render(request, 'polls/home.html')

def password_reset(request):
    return render(request, 'registration/password_reset_form.html')

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request):
    return render(request, 'registration/password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')


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

@login_required(login_url='/login')
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

@login_required(login_url='/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('polls:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'polls/change_password.html', {
        'form': form
    })

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def activate(request, uidb64, token, 
backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, 
backend='django.contrib.auth.backends.ModelBackend')
        return redirect('polls:dashboard')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required(login_url='/login')
def dashboard(request):
    # username = request.user
    # latest_question_list = Question.objects.exclude(username = username)

    # context = {
    #     'latest_question_list': latest_question_list,
    # }
    # return render(request, 'polls/dashboard.html',context)

    username = request.user
    latest_question_list = Question.objects.all().exclude(username=username)
    paginator = Paginator(latest_question_list,5) # 5 per page
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    context = {
        'questions':questions,
        'latest_question_list':latest_question_list
    }
    return render(request, 'polls/dashboard.html',context)


@login_required(login_url='/login')
def vote(request,question_id):
    username = request.user
    latest_question_list = Question.objects.all().exclude(username = username)
    paginator = Paginator(latest_question_list,5) # 5 per page
    page = request.GET.get('page')
    questions = paginator.get_page(page)
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
            'questions':questions,
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
                'questions':questions,
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
def surveys(request):
    username = request.user
    latest_survey_list = Surveytitle.objects.exclude(username = username)
    context = {
        'latest_survey_list': latest_survey_list,
    }
    return render(request, 'polls/surveys.html',context)

@login_required(login_url='/login')
def mysurveys(request):
    username = request.user
    latest_survey_list = Surveytitle.objects.filter(username = username)
    context = {
        'latest_survey_list': latest_survey_list,
    }
    return render(request, 'polls/mysurveys.html',context)

@login_required(login_url='/login')
def createsurveys(request,question_count):
    surveyformset = formset_factory(SurveyForm,extra=question_count)
    if request.method == 'POST':
        formset= surveyformset(request.POST)
        if formset.is_valid():
            i=0
            username = request.user
            survey = username.surveytitle_set.create(title = request.POST['title'],modified = request.POST['pub_date'])
            title = get_object_or_404(Surveytitle,title = request.POST['title'])
            for form in formset:
                questions = title.surveyquestion_set.create(question = request.POST['form-%d-question' % i],username = username)
                i=i+1
            return redirect('polls:mysurveys')
        else:
            return render(request,'polls/createsurveys.html', {"formset" : formset,"question_count" : question_count})
    else:
        formset = surveyformset()
    context = { 'formset' : formset,"question_count" : question_count}
    return render(request,'polls/createsurveys.html', context)

@login_required(login_url='/login')
def editsurvey(request,title_id):
    title = get_object_or_404(Surveytitle,pk=title_id)
    questions = title.surveyquestion_set.all()
    ordquestions = questions.order_by('id')
    initialquestiondata = ordquestions.values('question')
    surveyformset = formset_factory(SurveyForm,extra=0)
    if request.method == 'POST':
        formset = surveyformset(request.POST,initial=initialquestiondata)
        if formset.is_valid():
            if formset.has_changed():
                for i,question in zip(range(len(formset)),ordquestions):
                        surveyquestion = get_object_or_404(Surveyquestion,pk=question.id)
                        surveyquestion.question = request.POST['form-%d-question' % i]
                        surveyquestion.save()
                title.modified = request.POST['pub_date']
                title.save()
            else:
                print("No Change")
            return redirect('polls:mysurveys')
    else:
        formset = surveyformset(initial=initialquestiondata)
    context = { 'formset' : formset,'title_id' : title_id,'title' : title}
    return render(request,'polls/editsurvey.html', context)

@login_required(login_url='/login')
def deletesurvey(request,title_id):
    title = get_object_or_404(Surveytitle,pk=title_id)
    title.delete()
    return redirect('polls:mysurveys')

@login_required(login_url='/login')
def surveyresponse(request,title_id):
    username = request.user
    title = get_object_or_404(Surveytitle,pk=title_id)
    questions = title.surveyquestion_set.all()
    ordquestions = questions.order_by('id')
    initialquestiondata = ordquestions.values('question')
    answers = title.surveyanswer_set.filter(username=username)
    ordanswers = answers.order_by('id')
    initialanswerdata = ordanswers.values('answer')
    data=[]
    if len(initialanswerdata) != 0:
        for i,f in zip(initialquestiondata,initialanswerdata):
            z=dict(list(i.items()) + list(f.items()))
            data.append(z)
    else:
        for i in initialquestiondata:
            data.append(i)
    surveyformset = formset_factory(SurveyResponseForm,extra=0)
    if request.method == 'POST':
        formset = surveyformset(request.POST,initial=data)
        if formset.is_valid():
            if formset.has_changed():
                for i,question in zip(range(len(formset)),ordquestions):
                    surveyquestion = get_object_or_404(Surveyquestion,pk=question.id)
                    question.surveyanswer_set.create(title=question.title,answer=request.POST['form-%d-answer' % i],username = username)
                title.responses = title.responses + 1
                title.save()
            else:
                print("No Change")
            return redirect('polls:surveys')
    else:
        formset = surveyformset(initial=data)
    context = { 'formset' : formset,'title_id' : title_id,'title' : title}
    return render(request,'polls/surveyresponse.html', context)  

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
