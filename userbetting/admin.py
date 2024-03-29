from django.contrib import admin
from .forms import TeamForm


# Register your models here.
from .models import Game, Bet, Team, Tournament, Stage, Videogame, BettingGameGroup

admin.site.register(Tournament)
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Team)
admin.site.register(Stage)
admin.site.register(Videogame)
admin.site.register(BettingGameGroup)

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    fieldsets = (
        (None, {
            'fields': ('team_id', 'name', 'picture', 'colour')
            }),
        )