from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Submit,Row,Column,Div,HTML

from .models import PokemonOnTeam

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

class PokemonForm(ModelForm):
	class Meta:
		model = PokemonOnTeam
		exclude = ["team"]
		widgets = {
			"pokemon": forms.Select(attrs = {'onchange':"get_mon(this.value);"})
		}

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.helper = FormHelper()
		self.helper.form_show_labels = False
		self.helper.layout = Layout(
			Div(
				Row(
					Column(
						Row(
							Column(HTML('<p>Pokemon</p>')),
							Column('pokemon'),
							Column(HTML('<div id="pimg"></div>'))
						),
						'level','ability','tera_type'),
					Column(
						Row(
							Column(),
							Column(HTML('<p style="text-align: center;">EVs</p>')),
							Column(HTML('<p style="text-align: center;">IVs</p>'))
						),
						Row(
							Column(HTML('<p style="text-align: right;">HP</p>')),
							Column('ev_hp'),
							Column('iv_hp')
						),
						Row(
							Column(HTML('<p style="text-align: right;">Atk</p>')),
							Column('ev_atk'),
							Column('iv_atk')
						),
						Row(
							Column(HTML('<p style="text-align: right;">Def</p>')),
							Column('ev_def'),
							Column('iv_def')
						),
						Row(
							Column(HTML('<p style="text-align: right;">SpA</p>')),
							Column('ev_spa'),
							Column('iv_spa')
						),
						Row(
							Column(HTML('<p style="text-align: right;">SpD</p>')),
							Column('ev_spd'),
							Column('iv_spd')
						),
						Row(
							Column(HTML('<p style="text-align: right;">Spe</p>')),
							Column('ev_spe'),
							Column('iv_spe')
						),
						Row(
							Column(HTML('<p>Nature</p>')),
							Column('nature'),
						),
					),
					Column('move1','move2','move3','move4')
				),
				css_class="container"
			)
		)