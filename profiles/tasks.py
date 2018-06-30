from __future__ import absolute_import, unicode_literals
from DjangoTestProj1.celery import app
from .models import Profile
from operator import itemgetter

# @app.task
def rank_users_winnings():
    profiles = Profile.objects.all()

    list = []
    for profile in profiles:
        list.append((profile.user, profile.lifetime_winnings))
    list = sorted(list, key=itemgetter(1), reverse=True)
    ranking = 0
    for item in list:
        user = item[0]
        ranking += 1
        user.profile.ranking = ranking
        user.profile.total_number_users = len(list)

        user.profile.save()