from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from django.utils import timezone
from DjangoTestProj1.settings import MEDIA_URL
from community.models import CommunityGroup
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver

availiable_games = (
    ("csgo","cs:go"),
    ("sc2","starcraft"),
    ("lol","League of Legends"),
    ("dota","Dota 2"),
    ("overwatch","Overwatch")
)
# Create your models here.
class Videogame(models.Model):
    videogame_name = models.CharField(unique=True, max_length=30,
                              choices=availiable_games,
                              default="LoL")
    api_videogame_id = models.IntegerField(unique=True, null=True, blank=True)
    picture = models.ImageField(upload_to="teamLogos", null=True, blank=True)
    colour = models.CharField(max_length=7, null=False, blank=False, default="D3D3D3")
    alt_colour = models.CharField(max_length=7, null=False, blank=False, default="D3D3D3")

    def __str__(self):
        return self.videogame_name

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    api_team_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, null=False)
    picture = models.ImageField(upload_to="teamLogos", null=True, blank=True)
    picture_url = models.URLField(null=True,blank=True)
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
    # series on the API
    tournament_id = models.AutoField(primary_key=True)
    api_series_id = models.IntegerField(unique=False, null=True, blank=True)
    api_modified_at = models.DateTimeField('api_modified_at',null=True, blank=True)
    tournament_name = models.CharField(max_length=120, null=False, blank=False)

    groups = models.ManyToManyField(CommunityGroup,related_name='group_tournaments')

    videogame = models.ForeignKey(
        Videogame,
        related_name='videogame_tournaments',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )

    tournament_start_date = models.DateTimeField('Tournament start date')
    tournament_end_date = models.DateTimeField('Tournament end date', blank=True, null=True)


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

class Stage(models.Model):
    #tournament on the api
    stage_id = models.AutoField(primary_key=True)
    api_series_id = models.IntegerField(unique=False, null=True, blank=True)
    api_tournament_id = models.IntegerField(unique=True, null=True, blank=True)
    api_modified_at = models.DateTimeField('api_modified_at',null=True, blank=True)
    stage_name = models.CharField(max_length=120, null=False, blank=False)
    tournament = models.ForeignKey(Tournament, related_name='tournament_stages', blank=True, null=True, on_delete=models.PROTECT)
    stage_start_date = models.DateTimeField('Tournament start date')
    stage_end_date = models.DateTimeField('Tournament end date', blank=True, null=True)

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
        return self.stage_name

class Game(models.Model):
    # Match on the API
    game_id = models.AutoField(primary_key=True)
    api_match_id = models.IntegerField(unique=True,blank=True,null=True)
    api_modified_at = models.DateTimeField('api_modified_at',null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_b')
    videogame = models.ForeignKey(
        Videogame,
        related_name='videogame_games',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    stage = models.ForeignKey(Stage, related_name='stage_games', blank=True, null=True, on_delete=models.PROTECT)
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

    not_started = "not_started"
    starting = "Starting"
    running = "running"
    finished = "finished"
    finished_not_confirmed = "Finished - Not yet confirmed"
    finished_confirmed = "Finished - Confirmed"
    finished_paid = "Finished - All bets paid"

    availiable_statuses = ((not_started, "Not started"),
                           (starting, "Starting"),
                           (running, "Running"),
                           (finished, "Finished"),
                           (finished_not_confirmed, "Finished - Not yet confirmed"),
                           (finished_confirmed, "Finished - Confirmed"),
                           (finished_paid, "Finished - All bets paid"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=not_started)

    # Goal: Make it so that teamaa =/ team_b...
    # Useful thread = https://stackoverflow.com/questions/35096607/how-to-enforce-different-values-in-multiple-foreignkey-fields-for-django

    def save(self, *args, **kwargs):
        if self.team_a == self.team_b:
            raise Exception('attempted to create a match object where team_a == team_b')
        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.team_a) + " vs " + str(self.team_b) + " - " + str(self.game_date)

class BettingGameGroup(models.Model):
    betting_group_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, related_name='game_bgg', on_delete=models.PROTECT)
    group = models.ForeignKey(CommunityGroup, related_name='group_bgg', on_delete=models.PROTECT)

    active = "active"
    deactivated = "deactivated"

    availiable_statuses = ((active, "Active"),
                           (deactivated, "Deactivated"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=active,
                              null=False,
                              blank=False)
    class Meta:
        unique_together = ('game', 'group')

    def __str__(self):
        return str(self.group.name) + "'s betting group for : " + str(self.game.__str__())


class Bet(models.Model):
    bet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_bets', on_delete=models.PROTECT)
    betting_group = models.ForeignKey(BettingGameGroup, related_name='game_bets', on_delete=models.PROTECT)
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


@receiver(post_save, sender=Game)
def add_new_betting_groups(sender, instance, created, **kwargs):
    if created:
        groups = instance.tournament.groups.all()
        for group in groups:
            BettingGameGroup.objects.create(game=instance, group=group)


pre_save_groups = []

@receiver(post_save, sender=Tournament)
def add_existing_betting_groups(sender, instance, **kwargs):
    global pre_save_groups
    pre_save_groups = Tournament.objects.get(tournament_id=instance.tournament_id).groups.all()

@receiver(m2m_changed, sender=Tournament.groups.through)
def add_existing_betting_groups2(sender, instance, **kwargs):
    local_pre_save_groups = pre_save_groups
    # print(Tournament.objects.get(tournament_id=instance.tournament_id).groups.all())
    post_save_groups = instance.groups.all()

    if pre_save_groups != post_save_groups:
        print(local_pre_save_groups)
        print(post_save_groups)
        for group in post_save_groups:
            if group not in pre_save_groups:
                for game in instance.games.all():
                    betting_group, created_bgg = BettingGameGroup.objects.get_or_create(game=game, group=group)
                    if created_bgg == False:
                        betting_group.status = betting_group.active
                        betting_group.save()

        for group in pre_save_groups:
            if group not in post_save_groups:
                for betting_group in group.group_bgg.all():
                    #change to deactivate + hide?
                    betting_group.status = betting_group.deactivated
                    betting_group.save()