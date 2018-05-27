from django.contrib import admin

# Register your models here.
from .models import Game, Bet, Team

admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Team)