from django.conf import settings
from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from community.models import CommunityGroup
from django.utils import timezone
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
    groups = models.ManyToManyField(
        CommunityGroup,
        through='Wallet',
        through_fields=('profile', 'group'),
        related_name="profiles_groups"
    )
    groups_invited_to = models.ManyToManyField(
        CommunityGroup,
        through='CommunityInvite',
        through_fields=('profile', 'group'),
        related_name="profiles_invites"
    )

    def __str__(self):
        return self.user.username




class Wallet(models.Model):
    profile = models.ForeignKey(Profile, related_name='wallets_profile', blank=False, null=False, on_delete=models.PROTECT)
    group = models.ForeignKey(CommunityGroup, related_name='wallets_group', blank=False, null=False, on_delete=models.PROTECT)
    withdrawable_bank = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    non_withdrawable_bank = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ranking = models.IntegerField(default=0)
    founder = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    active = "active"
    deactivated = "deactivated"

    availiable_statuses = ((active, "Active"),
                           (deactivated, "Deactivated"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=active,
                              null=False,
                              blank=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Wallet, self).save(*args, **kwargs)


    @property
    def bank(self):
        return self.withdrawable_bank + self.non_withdrawable_bank

    @property
    def lifetime_winnings(self):
        bets = self.profile.user.user_bets.all()
        lifetime_winnings = 0
        for bet in bets:
            if bet.status == bet.paid:
                lifetime_winnings += bet.winnings
        return lifetime_winnings

    class Meta:
        unique_together = ('profile', 'group')

    def __str__(self):
        return str(self.profile.user.username) + "'s Wallet for: " + str(self.group.name)

class CommunityInvite(models.Model):
    profile = models.ForeignKey(Profile, related_name='community_invites_profile', blank=False, null=False, on_delete=models.PROTECT)
    group = models.ForeignKey(CommunityGroup, related_name='community_invites_group', blank=False, null=False, on_delete=models.PROTECT)
    inviter = models.ForeignKey(Profile, related_name='community_invites_inviter', blank=True, null=True, on_delete=models.PROTECT)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    sent = "sent"
    declined = "declined"
    declined_blocked = "declined_blocked"
    accepted = "accepted"

    availiable_statuses = ((sent, "Active"),
                           (declined, "Deactivated"),
                           (declined_blocked, "Declined and Blocked"),
                           (accepted, "Accepted"))

    status = models.CharField(max_length=30,
                              choices=availiable_statuses,
                              default=sent,
                              null=False,
                              blank=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(CommunityInvite, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('profile', 'group')

    def __str__(self):
        return str(self.profile.user.username) + ": invite for: " + str(self.group.name)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        group, c1 = CommunityGroup.objects.get_or_create(name="PUBLIC", daily_payout=50, removable= True)
        Wallet.objects.create(profile=profile, group=group)

# Update the number of users in a community group after wallet creation
@receiver(post_save, sender=Wallet)
def update_number_of_community_users(sender, instance, created, **kwargs):
    if created:
        community_group = instance.group
        number_of_users = len(community_group.profiles_groups.all())
        community_group.total_number_users = number_of_users
        community_group.save()