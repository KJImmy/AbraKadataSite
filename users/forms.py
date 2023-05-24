from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		fields = UserCreationForm.Meta.fields + ("email",)

class ShowdownUsernameForm(forms.Form):
	username = forms.CharField(label='Showdown Username',max_length=100)
	game1 = forms.URLField(label='Replay Link 1',max_length=1000)
	game2 = forms.URLField(label='Replay Link 2',max_length=1000)

class SubmitGameForm(forms.Form):
	game_link = forms.URLField(label='Replay Link',max_length=1000)

class ChangeEmailForm(forms.Form):
	email = forms.EmailField(label='New Email Address')