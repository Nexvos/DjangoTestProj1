from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User


# Create your models here.
class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True, null=False)

    def __str__(self):
        return self.name

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    team_a = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='%(class)s_team_b')
    game_date = models.DateTimeField('Game start date')
    not_begun = "not_begun"
    starting = "starting"
    ongoing = "ongoing"
    expected_duration = models.DurationField(default=timedelta(minutes=2))
    finished_not_confirmed = "finished_not_confirmed"
    finished_confirmed = "finished_confirmed"
    availiable_statuses = ((not_begun, "Not begun"),
                           (starting, "Starting"),
                           (ongoing, "Ongoing"),
                           (finished_not_confirmed, "Finished - Not yet confirmed"),
                           (finished_confirmed, "Finished - Confirmed"))
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
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    chosen_team = models.ForeignKey(Team, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # get first user (only user) associated with bet in case of deletion - Will this be needed or can I just make it so
    # that if a user wishes to delete their account that they'll just lock themselves out?

    # def get_original_user():


    def __str__(self):
        return str(self.game) + " | " + str(self.user) + " | £" + str(self.amount) +" bet for: " + str(self.chosen_team)