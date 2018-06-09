from django import forms

class ProfileForm(forms.Form):
    location = forms.CharField(max_length=120)
    picture = forms.ImageField()
    colour = forms.CharField(max_length=7)