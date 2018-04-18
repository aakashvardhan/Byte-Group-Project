from django import forms
from .models import SurveyChoice

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class SurveyForm(forms.ModelForm):
	class Meta:
		model = SurveyChoice
		fields = ('survey_text',)