from django.conf import settings
from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

User = settings.AUTH_USER_MODEL

def upload_location(instance, filename):

    location = instance.user.username
    return "%s/%s"%(location, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    location = models.CharField(max_length=120, null=True, blank=True)
    picture = models.ImageField(upload_to=upload_location,null=True,blank=True)
    colour = models.CharField(max_length=7, null=False, blank=False, default="D3D3D3")
    withdrawable_bank = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    non_withdrawable_bank = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ranking = models.IntegerField(default=0)
    total_number_users = models.IntegerField(default=0, editable=False)

    @property
    def bank(self):
        return self.withdrawable_bank + self.non_withdrawable_bank

    @property
    def lifetime_winnings(self):
        bets = self.user.bet_set.all()
        lifetime_winnings = 0
        for bet in bets:
            if bet.status == bet.paid:
                lifetime_winnings += bet.winnings
        return lifetime_winnings

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)