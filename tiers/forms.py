import datetime

from django.contrib.admin.widgets import AdminDateWidget
from django import forms

class FilterForm(forms.Form):
	start_date = forms.DateField(	required=False,
									widget=forms.SelectDateWidget(
										years=[2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023],
										empty_label=("Year","Month","Day")))
	end_date = forms.DateField(	required=False,
								widget=forms.SelectDateWidget(
									years=[2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023],
									empty_label=("Year","Month","Day")))
	minimum_rating = forms.IntegerField(required=False,min_value=1000)
	maximum_rating = forms.IntegerField(required=False,min_value=1000)