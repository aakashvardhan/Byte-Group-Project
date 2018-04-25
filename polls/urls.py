from django.urls import path,re_path, include

from django.contrib.auth import views as auth_views

from . import views

app_name = 'polls'

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.log_in, name='login'),
    path('logout/',views.log_out, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.register, name='register'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('password/',views.change_password, name='change_password'),
    path('accounts/password_reset/',views.password_reset,name='password_reset'),
    path('accounts/password_reset/done/',views.password_reset_done,name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',views.password_reset_confirm,name='password_reset_confirm'),
    path('accounts/reset/done/',views.password_reset_complete,name='password_reset_complete'),
    path('dashboard/vote/<int:question_id>/', views.vote, name='vote'),
    path('dashboard/mypolls/',views.mypolls, name='mypolls'),
    path('dashboard/surveys/',views.surveys, name='surveys'),
    path('dashboard/mysurveys',views.mysurveys, name='mysurveys'),
    path('dashboard/mysurveys/createsurveys/<int:question_count>',views.createsurveys, name='createsurveys'),
    path('dashboard/mysurveys/editsurvey/<int:title_id>',views.editsurvey, name='editsurvey'),
    path('dashboard/mysurveys/deletesurvey/<int:title_id>',views.deletesurvey, name='deletesurvey'),
    path('dashboard/surveys/surveyresponse/<int:title_id>',views.surveyresponse, name='surveyresponse'),
    path('dashboard/mysurveys/showresponders/<int:title_id>',views.showresponders, name='showresponders'),
    path('dashboard/mysurveys/showresponders/showresponse/<username>/<int:title_id>',views.showresponse, name='showresponse'),
    path('dashboard/createpolls/',views.createpolls, name='createpolls'),
    path('dashboard/createchoice/<int:question_id>',views.createchoice, name='createchoice'),
    path('dashboard/editpoll/<int:question_id>',views.editpoll, name='editpoll'),
    path('dashboard/editchoice/<int:choice_id>',views.editchoice, name='editchoice'),
    path('dashboard/deletechoice/<int:choice_id>',views.deletechoice, name='deletechoice'),
    path('dashboard/deletepoll/<int:question_id>',views.deletepoll, name='deletepoll'),
    path('ajax/validate_username',views.validate_username, name='validate_username'),
    path('dashboard/mypolls/chart/<int:question_id>',views.chart, name='chart'),
    path('dashboard/mypolls/chart/data/<int:question_id>',views.chartdata, name='chartdata'),
]
