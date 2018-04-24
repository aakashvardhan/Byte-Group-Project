from django.contrib import admin

from .models import Question, Choice,Votes,Surveytitle,Surveyquestion,Surveyanswer

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Votes)
admin.site.register(Surveytitle)
admin.site.register(Surveyquestion)
admin.site.register(Surveyanswer)