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
    path('ajax/validate_username',views.validate_username, name='validate_username'),
]
