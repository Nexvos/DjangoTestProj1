from django.contrib import admin

# Register your models here.
from .models import Game, Bet

admin.site.register(Game)
admin.site.register(Bet)