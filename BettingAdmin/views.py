from django.shortcuts import render
from userbetting.models import Game, Tournament, Team
from .adminBettingFunctions import get_future_match_data
from urllib import request
from django.core.files import File
import os
from datetime import datetime

# Create your views here.
def addTournament(request):
    data = get_future_match_data()

    for tournament in data:
        t1, created = Tournament.objects.get_or_create(
            api_tournament_id = tournament["tournament_id"],
            defaults={
                "tournament_name": tournament["series_name"] + " - " + tournament["tournament_name"],
                "tournament_start_date": datetime.strptime(
                    tournament["tournament_start_datetime"] ,
                    '%Y-%m-%dT%H:%M:%SZ'
                ),
                "tournament_end_date": datetime.strptime(
                    tournament["tournament_end_datetime"],
                    '%Y-%m-%dT%H:%M:%SZ'
                ),
                "api_modified_at": datetime.strptime(
                    tournament["modified_at"],
                    '%Y-%m-%dT%H:%M:%SZ'
                ),
                "videogame": tournament["tournament_videogame"]
            }
        )
        print(created)
        for match in tournament["matches"]:
            team_a, team_a_created = Team.objects.get_or_create(
                api_team_id = match["team_a_id"],
                defaults={
                    "name": match["team_a"],
                    "picture_url": match["team_a_img_url"],
            }
            )
            print(team_a_created)
            if team_a_created:
                try:
                    result = request.urlretrieve(team_a.picture_url)
                    team_a.save(
                        os.path.basename(team_a.picture_url),
                        File(open(result[0]))
                    )
                    team_a.save()
                except:
                    pass
            else:
                #check modified date and update image if it has changed
                pass
            team_b, team_b_created = Team.objects.get_or_create(
                api_team_id=match["team_b_id"],
                defaults={
                    "name": match["team_b"],
                    "picture_url": match["team_b_img_url"],
                }
            )
            print(team_b_created)
            if team_b_created:
                try:
                    result = request.urlretrieve(team_b.picture_url)
                    team_b.save(
                        os.path.basename(team_b.picture_url),
                        File(open(result[0]))
                    )
                    team_b.save()
                except:
                    pass
            else:
                # check modified date and update image if it has changed
                pass
            m1, match_created = Game.objects.get_or_create(
                api_match_id = match["match_id"],
                defaults={
                    "api_modified_at": datetime.strptime(
                        match["match_modified_datetime"],
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    "team_a": team_a,
                    "team_b": team_b,
                    "videogame": tournament["tournament_videogame"],
                    "tournament": t1,
                    "game_date": datetime.strptime(
                        match["match_start_datetime"],
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    "status": match["match_status"],
                    "winning_team": match["winner"]
                }
            )
            print(match_created)
    context = {
        'match_data':data
    }
    return render(request, 'BettingAdmin/add-tournament.html', context)