from django import forms
from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import Team

# class BetForm(forms.Form):
#     chosen_team = forms.charfield()


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'colour'}),
        }