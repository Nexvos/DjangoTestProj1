from django import forms
from decimal import Decimal
from .models import CommunityGroup

class CreateGroupForm(forms.Form):
    community_name = forms.CharField(max_length=120)
    invite_only = forms.BooleanField(required=False)
    members_can_invite = forms.BooleanField(required=False)
    header_background_colour = forms.CharField(max_length=7)
    header_text_colour = forms.CharField(max_length=7)
    tournaments = forms.CharField(required=False)
    daily_payout = forms.DecimalField(max_digits=7, decimal_places=2, min_value=Decimal('0.01'), required=False)

    def clean(self):
        cd = self.cleaned_data
        name = cd.get('community_name').lower()
        if "public" in name:
            self.add_error('community_name', "You cannot have the word 'public' in your community's name !")
        for t in CommunityGroup.objects.all():
            if name == t.name.lower():
                self.add_error('community_name', "The community name must be unique !")
        return cd

class UpdateGroupOptionsForm(forms.Form):
    invite_only = forms.BooleanField(required=False)
    members_can_invite = forms.BooleanField(required=False)
    header_background_colour = forms.CharField(max_length=7)
    header_text_colour = forms.CharField(max_length=7)
    daily_payout = forms.DecimalField(max_digits=7, decimal_places=2, min_value=Decimal('0.01'), required=False)

class InviteMembersForm(forms.Form):
    profile_id = forms.IntegerField(required=True)
