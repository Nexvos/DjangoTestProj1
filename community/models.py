from django.db import models


# Create your models here.
class CommunityGroup(models.Model):
    community_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=False, unique=True)
    private = models.BooleanField(default=False)
    daily_payout = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    removable = models.BooleanField(default=True)
    total_number_users = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.name



