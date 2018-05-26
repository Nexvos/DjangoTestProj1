from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User


# Create your models here.
class Game(models.Model):
    team_a = models.CharField(max_length=200)
    team_b = models.CharField(max_length=200)
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
    def __str__(self):
        return self.team_a + " vs " + self.team_b + " - " + str(self.game_date)

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Game, )
    chosen_team = models.CharField(max_length=30,
                              choices=teams)
    Amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)