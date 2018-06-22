from django import forms
from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import Team
from decimal import Decimal


class BetForm(forms.Form):
    chosen_team = forms.CharField(max_length=200)
    amount = forms.DecimalField(max_digits=7, decimal_places=2, min_value=Decimal('0.01'))


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'colour'}),
        }