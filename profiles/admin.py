from django.contrib import admin

# Register your models here.
from .models import Profile, Wallet, CommunityInvite

admin.site.register(Profile)
admin.site.register(Wallet)
admin.site.register(CommunityInvite)