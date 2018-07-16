import requests
from DjangoTestProj1.api_keys import getApiKey
import numpy as np
from PIL import Image, ImageDraw
import scipy
import scipy.misc
import scipy.cluster
from userbetting.models import Game, Tournament, Team
from urllib import request as urllib_request
from django.core.files import File
import os
from datetime import datetime
from datetime import timedelta
from django.conf import settings

# Account for pagination (read docs)

def get_new_API_data_by_videogame(game_id):
    url_base = "https://api.pandascore.co/"
    series_endpoint = "videogames/" + game_id + "/series.json?"
    tournaments_endpoint = "series/%s/tournaments.json?"
    matches_endpoint = "/tournaments/%s/matches.json?"
    optional_filter = "filter[name]=Overwatch&"
    api_key = "token=" + getApiKey()

    series_data_url = lambda: url_base + series_endpoint + api_key
    tournaments_data_url = lambda: url_base + tournaments_endpoint + api_key
    matches_data_url = lambda: url_base + matches_endpoint + api_key

    series_data = lambda: requests.get(series_data_url()).json()
    tournaments_data = lambda: requests.get(tournaments_data_url()).json()
    matches_data = lambda: requests.get(matches_data_url()).json()

    # PUBG 20
    # Overwatch 14
    # Dota 2 4
    # CS:GO 3
    # LoL 1

    # 2018-04-04T23:00:00Z
    loop = 0

    # return data if there is data availiable for team_a and team_b OR if the match ID is already stored in the database
    # -- Update if ID exists in database or create if it does not - update eneeds to search based on id for eaach match (no

    tournaments = []

    for i in series_data():
        try:
            datetime_object = datetime.strptime(i["end_at"], '%Y-%m-%dT%H:%M:%SZ')
            if datetime_object >= datetime.now():
                tournaments_endpoint = tournaments_endpoint % i["id"]
                for a in tournaments_data():
                    tournament_dict = {
                        "series_id": i["id"],
                        "series_name": i["name"],
                        "series_url": series_data_url(),
                        "series_start_datetime": i["begin_at"],
                        "series_end_datetime": i["end_at"],
                        "tournament_id": a["id"],
                        "tournament_name": a["name"],
                        "tournament_url": tournaments_data_url(),
                        "tournament_start_datetime": a["begin_at"],
                        "tournament_end_datetime": a["end_at"],
                        "modified_at": a["modified_at"],
                        "series_videogame": i["videogame"]["name"],
                        "tournament_videogame": a["videogame"]["name"],
                        "matches": []
                    }
                    if tournament_dict["series_name"] == "":
                        tournament_dict["series_name"] = i["slug"]

                    match_dicts = []
                    matches_endpoint = matches_endpoint % a["id"]
                    for b in matches_data():
                        try:
                            teams = [{
                                "name": b["opponents"][0]["opponent"]["name"],
                                "id": b["opponents"][0]["opponent"]["id"],
                                "image_url": b["opponents"][0]["opponent"]["image_url"]
                            },
                                {
                                "name": b["opponents"][1]["opponent"]["name"],
                                "id": b["opponents"][1]["opponent"]["id"],
                                "image_url": b["opponents"][1]["opponent"]["image_url"]
                            }]
                            teams.sort(key=lambda x: x["name"], reverse=False)
                            match_dict = {
                                "match_id": b["id"],
                                "match_name": b["name"],
                                "match_url": matches_data_url(),
                                "match_status": b["status"],
                                "match_start_datetime": b["begin_at"],
                                "match_modified_datetime": b["modified_at"],
                                "winner": b["winner"],
                                "team_a": teams[0]["name"],
                                "team_b": teams[1]["name"],
                                "team_a_id": teams[0]["id"],
                                "team_b_id": teams[1]["id"],
                                "team_a_img_url": teams[0]["image_url"],
                                "team_b_img_url": teams[1]["image_url"]
                            }
                            match_dicts.append(match_dict)
                        except:
                            pass
                    matches_endpoint = "/tournaments/%s/matches.json?"
                    if match_dicts != []:
                        tournament_dict["matches"] = match_dicts
                        tournaments.append(tournament_dict)
                tournaments_endpoint = "series/%s/tournaments.json?"
        except:
            pass

    return (tournaments)

def get_tournament_data_by_series_id(series_id):
    url_base = "https://api.pandascore.co/"

    tournaments_endpoint = "series/" + str(series_id) + "/tournaments.json?"
    matches_endpoint = "/tournaments/%s/matches.json?"
    optional_filter = "filter[name]=Overwatch&"
    api_key = "token=" + getApiKey()

    tournaments_data_url = lambda: url_base + tournaments_endpoint + api_key
    matches_data_url = lambda: url_base + matches_endpoint + api_key

    tournaments_data = lambda: requests.get(tournaments_data_url()).json()
    matches_data = lambda: requests.get(matches_data_url()).json()

    # return data if there is data availiable for team_a and team_b OR if the match ID is already stored in the database
    # -- Update if ID exists in database or create if it does not - update eneeds to search based on id for eaach match (no

    tournament = []

    for a in tournaments_data():
        tournament_dict = {
            "tournament_id": a["id"],
            "tournament_name": a["name"],
            "tournament_url": tournaments_data_url(),
            "tournament_start_datetime": a["begin_at"],
            "tournament_end_datetime": a["end_at"],
            "modified_at": a["modified_at"],
            "tournament_videogame": a["videogame"]["name"],
            "matches": []
        }

        match_dicts = []
        matches_endpoint = matches_endpoint % a["id"]
        for b in matches_data():
            try:
                teams = [{
                    "name": b["opponents"][0]["opponent"]["name"],
                    "id": b["opponents"][0]["opponent"]["id"],
                    "image_url": b["opponents"][0]["opponent"]["image_url"]
                },
                {
                    "name": b["opponents"][1]["opponent"]["name"],
                    "id": b["opponents"][1]["opponent"]["id"],
                    "image_url": b["opponents"][1]["opponent"]["image_url"]
                }]
                teams.sort(key=lambda x: x["name"], reverse=False)
                match_dict = {
                    "match_id": b["id"],
                    "match_name": b["name"],
                    "match_url": matches_data_url(),
                    "match_status": b["status"],
                    "match_start_datetime": b["begin_at"],
                    "match_modified_datetime": b["modified_at"],
                    "winner": b["winner"],
                    "team_a": teams[0]["name"],
                    "team_b": teams[1]["name"],
                    "team_a_id": teams[0]["id"],
                    "team_b_id": teams[1]["id"],
                    "team_a_img_url": teams[0]["image_url"],
                    "team_b_img_url": teams[1]["image_url"]
                }
                match_dicts.append(match_dict)
            except:
                pass
        matches_endpoint = "/tournaments/%s/matches.json?"
        if match_dicts != []:
            tournament_dict["matches"] = match_dicts
            tournament.append(tournament_dict)

    return (tournament)

def get_match_data_by_tournament_id(tournament_id):
    url_base = "https://api.pandascore.co/"

    matches_endpoint = "/tournaments/" + str(tournament_id) + "/matches.json?"
    optional_filter = "filter[name]=Overwatch&"
    api_key = "token=" + getApiKey()

    matches_data_url = lambda: url_base + matches_endpoint + api_key

    matches_data = lambda: requests.get(matches_data_url()).json()

    # return data if there is data availiable for team_a and team_b OR if the match ID is already stored in the database
    # -- Update if ID exists in database or create if it does not - update eneeds to search based on id for eaach match (no


    match_dicts = []
    for b in matches_data():
        try:
            teams = [{
                "name": b["opponents"][0]["opponent"]["name"],
                "id": b["opponents"][0]["opponent"]["id"],
                "image_url": b["opponents"][0]["opponent"]["image_url"]
            },
            {
                "name": b["opponents"][1]["opponent"]["name"],
                "id": b["opponents"][1]["opponent"]["id"],
                "image_url": b["opponents"][1]["opponent"]["image_url"]
            }]
            teams.sort(key=lambda x: x["name"], reverse=False)
            match_dict = {
                "match_id": b["id"],
                "match_name": b["name"],
                "match_url": matches_data_url(),
                "match_status": b["status"],
                "match_start_datetime": b["begin_at"],
                "match_modified_datetime": b["modified_at"],
                "winner_id": b["winner"]["id"],
                "winner": b["winner"]["name"],
                "team_a": teams[0]["name"],
                "team_b": teams[1]["name"],
                "team_a_id": teams[0]["id"],
                "team_b_id": teams[1]["id"],
                "team_a_img_url": teams[0]["image_url"],
                "team_b_img_url": teams[1]["image_url"]
            }
            match_dicts.append(match_dict)
        except:
            pass

    return (match_dicts)

def get_colors(file_location):
    NUM_CLUSTERS = 10

    print('reading image')

    im = Image.open(file_location)
    im = im.resize((150, 150))  # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    print('finding clusters')

    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    print('cluster centres:\n', codes)


    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))  # count occurrences

    print(np.argsort(-(counts), axis=0)[0])
    print(scipy.argmax(counts))
    index_max = np.argsort(-(counts), axis=0)[0]  # find most frequent


    peak = codes[index_max]
    try:
        if peak[3] < 50.0:
            peak = codes[np.argsort(-(counts), axis=0)[1]]
    except:
        pass
    print(peak)
    colour = '%02x%02x%02x' % (int(peak[0]), int(peak[1]), int(peak[2]))
    print('most frequent is %s (#%s)' % (peak, colour))
    return(colour)

def Add_new_tournament(game_id):
    data = get_new_API_data_by_videogame(game_id)

    for tournament in data:
        t1, created = Tournament.objects.get_or_create(
            api_tournament_id=tournament["tournament_id"],
            api_series_id=tournament["series_id"],
            defaults={
                "tournament_name": tournament["series_name"] + " - " + tournament["tournament_name"],
                "tournament_start_date": datetime.strptime(
                    tournament["tournament_start_datetime"],
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

        for match in tournament["matches"]:
            team_a, team_a_created = Team.objects.get_or_create(
                api_team_id=match["team_a_id"],
                defaults={
                    "name": match["team_a"],
                    "picture_url": match["team_a_img_url"]
                }
            )

            if team_a_created:
                try:
                    result = urllib_request.urlretrieve(team_a.picture_url)
                    team_a.picture.save(
                        os.path.basename(team_a.picture_url),
                        File(open(result[0], "rb"))
                    )
                    team_a.save()
                except:
                    pass
                try:
                    team_a.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_a.picture)))
                    team_a.save()
                except:
                    pass
            else:
                # update image if image doesn't exist or image has been updated?
                pass
            team_b, team_b_created = Team.objects.get_or_create(
                api_team_id=match["team_b_id"],
                defaults={
                    "name": match["team_b"],
                    "picture_url": match["team_b_img_url"]
                }
            )

            if team_b_created:
                try:
                    result = urllib_request.urlretrieve(team_b.picture_url)
                    team_b.picture.save(
                        os.path.basename(team_b.picture_url),
                        File(open(result[0], "rb"))
                    )
                    team_b.save()
                except:
                    pass
                try:
                    team_b.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_b.picture)))
                    team_b.save()
                except:
                    pass
            else:
                # update image if image doesn't exist or image has been updated?
                pass

            m1, match_created = Game.objects.get_or_create(
                api_match_id=match["match_id"],
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

def mark_tournaments_complete():
    tournaments = Tournament.objects.all()
    for tournament in tournaments:
        # games = Game.objects.filter(tournament__tournament_id=tournament.tournament_id)
        if tournament.status != tournament.finished:
            if datetime.now() >= (tournament.tournament_end_date + timedelta(days=1)):
                tournament.status = tournament.finished
                tournament.save()
            elif datetime.now() >= tournament.tournament_start_date:
                tournament.status = tournament.ongoing
                tournament.save()

def update_existing_tournaments():

    # get tournament_ids and match_ids for models
    # get data for each tournament and match - check modified date if it is > than existing date then check for updates

    #tests
        # What if a tournament adds new games? will these be added?
        # Will updating an existing match update the model in the db? tournament update?
        # Will matches get updated if their status is finished - bets paid?
        # If modify data changes but no other data, does the data change in anyway upon an update?
        # Do the date ifs work? if the data modified hasn't changed do they still activate?

    # Get all tournamnts in the daatabase
    tournaments = Tournament.objects.all()

    #iterate throught each tournament in the database
    for tournament in tournaments:

        print(str(tournament.tournament_name) + " is now updating")

        #if the tournament is finished we don't want to be pinging the API for changes
        if tournament.status != tournament.finished:
            print("    Tournament is not finished")

            # data is fetched for each tournament from the API based on the API tournament ID
            tournament_data = get_tournament_data_by_series_id(tournament.api_series_id)
            for item in tournament_data:
                if item["tournament_id"] == tournament.api_tournament_id:
                    tournament_dict = item

            # only update the tournament if data exists for that tournamnent
            if 'tournament_dict' in locals():
                match_data = get_match_data_by_tournament_id(tournament.api_tournament_id)

                # The list of games associated with the tournament is fetched
                games = Game.objects.filter(tournament__api_tournament_id=tournament.api_tournament_id)

                #create empty array for game ID's this will allow us to create new games in the database later based
                # on match_id's found through the API that aren't in the DB
                database_games = []

                #modified datetime on the API is converted to a python datetime for calculations below
                # try statement is due to the api being shit and not populating modified dates
                try:
                    tournament_modified_datetime = datetime.strptime(
                        tournament_dict["modified_at"],
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                except:
                    tournament_modified_datetime = "None"

                print("    database modified date: " + str(tournament.api_modified_at))
                print("    API modified date: " + str(tournament_modified_datetime))

                #update tournment details
                print("    ...Database being updated")

                # check the date is a date...
                if tournament_modified_datetime != "None":
                    #update the database modified date
                    print("modified date exists!!!!")
                    tournament.api_modified_at = tournament_modified_datetime

                #datetime on the API is converted to a python datetime for calculations below
                tournament_start_date = datetime.strptime(
                    tournament_dict["tournament_start_datetime"],
                    '%Y-%m-%dT%H:%M:%SZ'
                )
                # datetime on the API is converted to a python datetime for calculations below
                tournament_end_date = datetime.strptime(
                    tournament_dict["tournament_end_datetime"],
                    '%Y-%m-%dT%H:%M:%SZ'
                )
                # if the tournament start date is different on the API (compared to the DB)then update the database
                if tournament.tournament_start_date != tournament_start_date:
                    tournament.tournament_start_date = tournament_start_date
                    print("    startdate changed")

                # if the tournament end date is different on the API (compared to the DB)then update the database value
                if tournament.tournament_end_date != tournament_end_date:
                    tournament.tournament_end_date = tournament_end_date
                    print("    enddate changed")

                # save the tournament modified date + start and end date if they've changed
                tournament.save()

                print("    iterating through tournament games:")
                # iterate through each game associated with the tournament
                for game in games:

                    print("database match id: " + str(game.api_match_id))
                    # Add the API match_id for each game to a list for comparison with games located on the API later
                    database_games.append(game.api_match_id)

                    # iterate through each game associated with the API tournament on the API
                    for api_game in match_data:
                        print("  api match id: " + str(api_game["match_id"]))
                        # modified datetime on the API is converted to a python datetime for calculations below
                        try:
                            match_modified_datetime = datetime.strptime(
                                api_game["match_modified_datetime"],
                                '%Y-%m-%dT%H:%M:%SZ'
                            )
                        except:
                            match_modified_datetime = "None"



                        # used for debugging - please delete after
                        if game.api_match_id == api_game["match_id"] and (match_modified_datetime >= game.api_modified_at or match_modified_datetime == "None"):
                            print("      database_api_match_id: " + str(game.api_match_id))
                            print("      api_match_id: " + str(api_game["match_id"]))

                        # if the saved api id in the database matches the api id on the api AND the modified date has
                        # changed, then make changes to/ update the game in the database
                        if game.api_match_id == api_game["match_id"] and (match_modified_datetime >= game.api_modified_at or match_modified_datetime == "None"):
                            # update the game modified date
                            if match_modified_datetime != "None":
                                game.api_modified_at = match_modified_datetime

                            # if team a's ids are identical and either the name or image url have changed then update them
                            if game.team_a.api_team_id == api_game["team_a_id"] and (
                                    game.team_a.name != api_game["team_a"] or
                                    game.team_a.picture_url != api_game["team_a_img_url"]
                            ):
                                game.team_a.name = api_game["team_a"]
                                game.team_a.picture_url = api_game["team_a_img_url"]
                                game.team_a.save()
                                print("      team a already exists and has been updated")
                            # if team_a's api id saved in the database isn't the same as the api team id then either
                            # get the team from the database or create a new team
                            elif game.team_a.api_team_id != api_game["team_a_id"]:
                                team_a, team_a_created = Team.objects.get_or_create(
                                    api_team_id=api_game["team_a_id"],
                                    defaults={
                                        "name": api_game["team_a"],
                                        "picture_url": api_game["team_a_img_url"]
                                    }
                                )


                                # if team_a was created then the team picture is downloaded and saved and dominant
                                # colour is calculated
                                if team_a_created:
                                    print("      team a has changed - a new team was created in the database")
                                    # download team picture and save
                                    try:
                                        result = urllib_request.urlretrieve(team_a.picture_url)
                                        team_a.picture.save(
                                            os.path.basename(team_a.picture_url),
                                            File(open(result[0], "rb"))
                                        )
                                        team_a.save()
                                    # exception in case of failure - Need to consider how to handle failures
                                    except:
                                        pass

                                    # Find the most dominant colour in the team picture and set it as the team colour
                                    try:
                                        team_a.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_a.picture)))
                                        team_a.save()
                                    # exception in case of failure - Need to consider how to handle failures
                                    except:
                                        pass
                                else:
                                    print("      team a has changed to another team in the database")
                                    # update image if image doesn't exist or image has been updated?
                                    pass

                                # set the first team to the newly fetched or created team
                                game.team_a = team_a



                            #if team b's ids are identical and either the name or image url have changed then update them
                            if game.team_b.api_team_id == api_game["team_b_id"] and (
                                    game.team_b.name != api_game["team_b"] or
                                    game.team_b.picture_url != api_game["team_b_img_url"]
                            ):
                                game.team_b.name = api_game["team_b"]
                                game.team_b.picture_url = api_game["team_b_img_url"]
                                game.team_b.save()
                                print("      team b already exists and has been updated")

                            # if team_b's api id saved in the database isn't the same as the api team id then either
                            # get the team from the database or create a new team
                            elif game.team_b.api_team_id != api_game["team_b_id"]:
                                team_b, team_b_created = Team.objects.get_or_create(
                                    api_team_id=api_game["team_b_id"],
                                    defaults={
                                        "name": api_game["team_b"],
                                        "picture_url": api_game["team_b_img_url"]
                                    }
                                )
                                print(team_b_created)

                                # if team_b was created then the team picture is downloaded and saved and dominant
                                # colour is calculated
                                if team_b_created:
                                    print("      team b has changed - a new team was created in the database")
                                    # download team picture and save
                                    try:
                                        result = urllib_request.urlretrieve(team_b.picture_url)
                                        team_b.picture.save(
                                            os.path.basename(team_b.picture_url),
                                            File(open(result[0], "rb"))
                                        )
                                        team_b.save()
                                    # exception in case of failure - Need to consider how to handle failures
                                    except:
                                        pass

                                    # Find the most dominant colour in the team picture and set it as the team colour
                                    try:
                                        team_b.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_b.picture)))
                                        team_b.save()

                                    # exception in case of failure - Need to consider how to handle failures
                                    except:
                                        pass
                                else:
                                    print("      team b has changed to another team in the database")
                                    # update image if image doesn't exist or image has been updated?
                                    pass

                                # set the second team to the newly fetched or created team
                                game.team_b = team_b

                            game.game_date = datetime.strptime(
                                api_game["match_start_datetime"],
                                '%Y-%m-%dT%H:%M:%SZ'
                            )
                            print(api_game["match_status"])
                            game.status = api_game["match_status"]
                            game.winning_team = api_game["winner"]
                            game.save()
                            print("status should be updated!!!!!!!!!")

                # Figure out games in api_games not in database_games and create those games
                for api_game in match_data:
                    if api_game["match_id"] not in database_games:
                        print("    new match found without existing database copy: " + str(api_game["match_id"]))
                        team_a, team_a_created = Team.objects.get_or_create(
                            api_team_id=api_game["team_a_id"],
                            defaults={
                                "name": api_game["team_a"],
                                "picture_url": api_game["team_a_img_url"]
                            }
                        )

                        if team_a_created:
                            try:
                                result = urllib_request.urlretrieve(team_a.picture_url)
                                team_a.picture.save(
                                    os.path.basename(team_a.picture_url),
                                    File(open(result[0], "rb"))
                                )
                                team_a.save()
                            except:
                                pass
                            try:
                                team_a.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_a.picture)))
                                team_a.save()
                            except:
                                pass
                        else:
                            # update image if image doesn't exist or image has been updated?
                            pass
                        team_b, team_b_created = Team.objects.get_or_create(
                            api_team_id=api_game["team_b_id"],
                            defaults={
                                "name": api_game["team_b"],
                                "picture_url": api_game["team_b_img_url"]
                            }
                        )

                        if team_b_created:
                            try:
                                result = urllib_request.urlretrieve(team_b.picture_url)
                                team_b.picture.save(
                                    os.path.basename(team_b.picture_url),
                                    File(open(result[0], "rb"))
                                )
                                team_b.save()
                            except:
                                pass
                            try:
                                team_b.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team_b.picture)))
                                team_b.save()
                            except:
                                pass
                        else:
                            # update image if image doesn't exist or image has been updated?
                            pass

                        m1, match_created = Game.objects.get_or_create(
                            api_match_id=api_game["match_id"],
                            defaults={
                                "api_modified_at": datetime.now(),
                                "team_a": team_a,
                                "team_b": team_b,
                                "videogame": tournament.videogame,
                                "tournament": tournament,
                                "game_date": datetime.strptime(
                                    api_game["match_start_datetime"],
                                    '%Y-%m-%dT%H:%M:%SZ'
                                ),
                                "status": api_game["match_status"],
                                "winning_team": api_game["winner"]
                            }
                        )
            else:
                #delete the tournament from db as it no longer exists? Set it to inactive? Mark as something?
                print("tournament no longer exists")
                pass