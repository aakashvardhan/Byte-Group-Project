from django.db import models

from django.utils import timezone

from django.contrib.auth.models import User

import datetime

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text

class SurveyChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    survey_text = models.CharField(max_length=200)

    def __str__(self):
        return self.survey_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Votes(models.Model):
    username = models.CharField(max_length=20)
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.username
