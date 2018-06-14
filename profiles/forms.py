from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.urls import reverse

class ProfileForm(forms.Form):
    location = forms.CharField(max_length=120)
    picture = forms.ImageField()
    colour = forms.CharField(
        max_length=7,
        widget=forms.TextInput(
            attrs={
                "class": "jscolor",
                "value": "AB2567"
            }
        )
    )
    # Uni-form
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_tag = False
        self.helper.layout = Layout(
            Field('location', css_class='input-xlarge'),
            Field('colour', css_class='jscolor'),
            Div(Field('picture', css_class='custom-file-input'), css_class="custom-file"),
            # AppendedText('appended_text', '.00'),
            FormActions(
                Submit('save_changes', 'Save changes', css_class="btn btn-primary"),
            )
        )