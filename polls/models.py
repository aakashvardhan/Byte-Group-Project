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

class Survey(models.Model):
    title = models.CharField(max_length=50)
    modified = models.DateTimeField('date modified')
    responses = models.IntegerField(default=0)
    username = models.ForeignKey(User,null=True,on_delete=models.CASCADE)

    def was_modified_recently(self):
        return self.modified >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.title

class Surveyquestion(models.Model):
    title = models.ForeignKey(Survey,on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    username = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.question

class Surveyanswer(models.Model):
    question = models.ForeignKey(Surveyquestion,on_delete=models.CASCADE)
    answer = models.TextField()
    username = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.answer




