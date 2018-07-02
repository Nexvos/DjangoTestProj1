from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from django.utils import timezone

availiable_games = (
    ("CSGO","cs:go"),
    ("SC2","starcraft"),
    ("LOL","League of Legends"),
    ("Dota","Dota 2"),
    ("Overwatch","Overwatch")
)
# Create your models here.

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True, null=False)
    picture = models.ImageField(upload_to="teamLogos", null=True, blank=True)
    colour = models.CharField(max_length=7, null=False, blank=False, default="D3D3D3")

    @property
    def colour_rgb(self):
        rgb_str = str((tuple(int(self.colour[i:i+2], 16) for i in (0, 2 ,4))))
        rgb_str = rgb_str.rstrip(")")
        rgb_str = rgb_str.lstrip("(")
        return rgb_str

    @property
    def colour_rgb_whitened(self):
        rgb_str = (tuple(int(self.colour[i:i + 2], 16) for i in (0, 2, 4)))
        white = (255,255,255)
        whitened_value = str(((rgb_str[0]+white[0])/2,(rgb_str[1]+white[1])/2,(rgb_str[2]+white[2])/2))
        whitened_value = whitened_value.rstrip(")")
        whitened_value = whitened_value.lstrip("(")
        return whitened_value

    def __str__(self):
        return self.name



class Tournament(models.Model):
    tournament_id = models.AutoField(primary_key=True)
    tournament_name = models.CharField(max_length=120, null=False, blank=False, unique=True)
    videogame = models.CharField(max_length=30,
                              choices=availiable_games,
                              default="cs:go")

    tournament_start_date = models.DateTimeField('Tournament start date')
    tournament_send_date = models.DateTimeField('Tournament end date')


    main_twitch_url =  models.URLField(max_length=200, unique=True, blank=True, null=True)

    not_begun = "Not begun"
    ongoing = "Ongoing"
    finished = "Finished"


    availiable_statuses = ((not_begun, "Not begun"),
                           (ongoing, "Ongoing"),
                           (finished, "Finished"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=not_begun)

    def __str__(self):
        return self.tournament_name

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    team_a = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_b')
    videogame = models.CharField(max_length=30,
                                 choices=availiable_games,
                                 blank=True, null=True,)
    tournament = models.ForeignKey(Tournament, related_name='games', blank=True, null=True, on_delete=models.PROTECT)
    game_date = models.DateTimeField('Game start date')

    team_a_winner = "Team A is the winner"
    team_b_winner = "Team B is the winner"
    not_decided = "Not Decided"
    teams = ((not_decided, "Not Decided"),
             (team_a_winner, "Team A is the winner"),
             (team_b_winner, "Team B is the winner"))

    winning_team = models.CharField(max_length=60,
                                    choices=teams,
                                    default= not_decided,
                                    unique=False,
                                    blank=True,
                                    null=True)

    twitch_url =  models.URLField(max_length=200, unique=True, blank=True, null=True)
    expected_duration = models.DurationField(default=timedelta(minutes=2))

    not_begun = "Not begun"
    starting = "Starting"
    ongoing = "Ongoing"
    finished_not_confirmed = "Finished - Not yet confirmed"
    finished_confirmed = "Finished - Confirmed"
    finished_paid = "Finished - All bets paid"

    availiable_statuses = ((not_begun, "Not begun"),
                           (starting, "Starting"),
                           (ongoing, "Ongoing"),
                           (finished_not_confirmed, "Finished - Not yet confirmed"),
                           (finished_confirmed, "Finished - Confirmed"),
                           (finished_paid, "Finished - All bets paid"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=not_begun)

    # Goal: Make it so that teamaa =/ team_b...
    # Useful thread = https://stackoverflow.com/questions/35096607/how-to-enforce-different-values-in-multiple-foreignkey-fields-for-django

    def save(self, *args, **kwargs):
        if self.team_a == self.team_b:
            raise Exception('attempted to create a match object where team_a == team_b')
        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.team_a) + " vs " + str(self.team_b) + " - " + str(self.game_date)


class Bet(models.Model):
    bet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_bets', on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name='game_bets', on_delete=models.PROTECT)
    chosen_team = models.ForeignKey(Team, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    open = "Open"
    lost = "Lost"
    paid = "Paid"

    availiable_statuses = ((open, "Open"),
                           (lost, "Lost"),
                           (paid, "Paid"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=open)

    winnings = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.bet_id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)


    def __str__(self):
        return str(self.game) + " | " + str(self.user) + " | £" + str(self.amount) +" bet for: " + str(self.chosen_team)
