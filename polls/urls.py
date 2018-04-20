from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.log_in, name='login'),
    path('logout/',views.log_out, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.register, name='register'),
    path('dashboard/vote/<int:question_id>/', views.vote, name='vote'),
    path('dashboard/mypolls/',views.mypolls, name='mypolls'),
    path('dashboard/mysurvey/', views.mysurvey, name='mysurvey'),
    path('dashboard/createsurvey/', views.createsurvey, name='createsurvey'),
    path('dashboard/createpolls/',views.createpolls, name='createpolls'),
    path('dashboard/createchoice/<int:question_id>',views.createchoice, name='createchoice'),
    path('dashboard/editpoll/<int:question_id>',views.editpoll, name='editpoll'),
    path('dashboard/editchoice/<int:choice_id>',views.editchoice, name='editchoice'),
    path('dashboard/deletepoll/<int:question_id>',views.deletepoll, name='deletepoll'),
    path('ajax/validate_username',views.validate_username, name='validate_username'),
]
