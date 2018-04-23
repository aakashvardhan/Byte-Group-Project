from django.urls import path,re_path

from . import views

app_name = 'polls'

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.log_in, name='login'),
    path('logout/',views.log_out, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.register, name='register'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('dashboard/vote/<int:question_id>/', views.vote, name='vote'),
    path('dashboard/mypolls/',views.mypolls, name='mypolls'),
    path('dashboard/mysurvey/', views.mysurvey, name='mysurvey'),
    path('dashboard/createsurvey/', views.createsurvey, name='createsurvey'),
    path('dashboard/deletesurvey/<int:survey_id>', views.deletesurvey, name='deletesurvey'),
    path('dashboard/editsurvey/<int:survey_id>', views.editsurvey, name='editsurvey'),
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
