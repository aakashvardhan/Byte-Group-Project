from django.contrib import admin

from .models import Question, Choice,Votes, Survey

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Votes)
admin.site.register(Survey)