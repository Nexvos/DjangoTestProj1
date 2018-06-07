from django import forms

class BetForm(forms.Form):
    chosen_team = forms.charfield()
