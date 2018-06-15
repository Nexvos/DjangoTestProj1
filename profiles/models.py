from django.conf import settings
from django.db import models


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
    bank = models.DecimalField(max_digits=6, decimal_places=2, default=0)


    def __str__(self):
        return self.user.username
