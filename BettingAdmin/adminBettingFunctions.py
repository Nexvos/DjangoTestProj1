import requests
from DjangoTestProj1.api_keys import getApiKey
import numpy as np
from PIL import Image, ImageDraw
import scipy
import scipy.misc
import scipy.cluster
from userbetting.models import Game, Tournament, Team, Stage, Videogame
from urllib import request as urllib_request
from django.core.files import File
import os
from datetime import datetime
from datetime import timedelta
from django.conf import settings


def get_data(url_without_page):
    # Variables
    api_key = "token=" + getApiKey() # gets the API key from a function hidden from GIT
    page_filter = "page[number]="
    page_number = 1 # page number starts at 1 and will increase. page 0 is a duplicate of page 1 so is not considered

    # url function - constructed as a lambda function so that it can be recalculated as page_number changes
    url = lambda: url_without_page + page_filter + str(page_number) + "&page[size]=100&" + api_key

    # Initialise data variable as an empty array
    data = []
    # page_data is set to True so the while loop will start - This could be anything as it gets redeclared in the loop
    page_data = True

    # Once the loop reaches a page with no data the function will stop fetching data
    while page_data != []:
        page_data = requests.get(url()).json() # JSON data is fetched for the url and page number specified

        # Each dictionary in the fetched array is appended to the data array
        for i in page_data:
            data.append(i)
        if len(page_data) != 100:
            break
        page_number = page_number + 1 # Page number is increased by 1 so the loop can fetch the next pages data

    pages_with_data = page_number # is the number of pages with data

    page_number = 1 # Reset to 1 so the output url below will point to the first page

    #remove api key from variable so the output url doesn't contain the key
    api_key = "token="

    # returns a tuple of information. [0] is the data [1] is the number of pages with data and [2] is the url
    return data, pages_with_data, url()

def get_match_data_by_tournament_id(tournament_id):
    #variables
    url_base = "https://api.pandascore.co/"
    matches_endpoint = "/tournaments/" + str(tournament_id) + "/matches.json?"
    match_data_url = url_base + matches_endpoint

    match_data = get_data(match_data_url)

    # initialise the series array - this will hold the data the function returns
    matches = []

    # save the current time to avoid this function being called multiple times and errors occuring
    time_now = datetime.now()

    # The matches data is looped
    for b in match_data[0]:
        # try statement in case of bad data
        try:
            # separate teams dict is created so the teams can be alaphabetically sorted
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
            # teams alphabetically sorted
            teams.sort(key=lambda x: x["name"], reverse=False)

            # Convert the start datetime to a python value or set it to None if it doesn't exist
            if b["begin_at"] == None or b["begin_at"] == "":
                match_start_datetime = None
            else:
                match_start_datetime = datetime.strptime(b["begin_at"], '%Y-%m-%dT%H:%M:%SZ')

            # Convert the modified datetime to a python value or set it to None if it doesn't exist
            if b["modified_at"] == None or b["modified_at"] == "":
                match_modified_datetime = None
            else:
                match_modified_datetime = datetime.strptime(b["modified_at"], '%Y-%m-%dT%H:%M:%SZ')

            # match dict created with match level detail
            match_dict = {
                "match_id": b["id"],
                "match_name": b["name"],
                "match_url": match_data[2],
                "match_status": b["status"],
                "match_start_datetime": match_start_datetime,
                "match_modified_datetime": match_modified_datetime,
                "winner": b["winner"],
                "team_a": teams[0]["name"],
                "team_b": teams[1]["name"],
                "team_a_id": teams[0]["id"],
                "team_b_id": teams[1]["id"],
                "team_a_img_url": teams[0]["image_url"],
                "team_b_img_url": teams[1]["image_url"]
            }

            matches.append(match_dict)
        except:
            pass

    return matches, match_data[1], match_data[2]

def get_new_tournament_data_by_series_id(series_id):
    #variables
    url_base = "https://api.pandascore.co/"
    tournaments_endpoint = "series/" + str(series_id) + "/tournaments.json?"
    tournaments_data_url = url_base + tournaments_endpoint
    tournaments_data = get_data(tournaments_data_url)

    # initialise the series array - this will hold the data the function returns
    tournaments = []

    # save the current time to avoid this function being called multiple times and errors occuring
    time_now = datetime.now()

    # Loop through the series' fetched by the get_data function above
    for a in tournaments_data[0]:
        try:
            tournament_start_datetime = datetime.strptime(a["begin_at"], '%Y-%m-%dT%H:%M:%SZ')

            # Convert the end datetime to a python value or set it to None if it doesn't exist
            if a["end_at"] == None or a["end_at"] == "":
                tournament_end_datetime = None
            else:
                tournament_end_datetime = datetime.strptime(a["end_at"], '%Y-%m-%dT%H:%M:%SZ')

            if tournament_start_datetime >= time_now or (tournament_end_datetime >= time_now) if tournament_end_datetime != None else False:

                # the api doesn't always have the name field populated - this function uses the slug field if that's the case
                if a["name"] == None or a["name"] == "":
                    tournament_name = a["slug"]
                else:
                    tournament_name = a["name"]

                # The matches data for the tournament is saved to a variable for later use
                match_data_saved = get_match_data_by_tournament_id(a["id"])

                # tournament dict created with tournament level detail
                tournament_dict = {
                    "tournament_id": a["id"],
                    "tournament_name": tournament_name,
                    "tournament_url": tournaments_data[2],
                    "tournament_start_datetime": tournament_start_datetime,
                    "tournament_end_datetime": tournament_end_datetime,
                    "tournament_videogame": a["videogame"]["name"],
                    "matches": match_data_saved[0]
                }

                tournaments.append(tournament_dict)
        except:
            pass
    return tournaments, tournaments_data[1], tournaments_data[2]

def get_all_tournament_data_by_series_id(series_id):
    #variables
    url_base = "https://api.pandascore.co/"
    tournaments_endpoint = "series/" + str(series_id) + "/tournaments.json?"
    tournaments_data_url = url_base + tournaments_endpoint
    tournaments_data = get_data(tournaments_data_url)

    # initialise the series array - this will hold the data the function returns
    tournaments = []

    # save the current time to avoid this function being called multiple times and errors occuring
    time_now = datetime.now()

    # Loop through the series' fetched by the get_data function above
    for a in tournaments_data[0]:
        try:
            tournament_start_datetime = datetime.strptime(a["begin_at"], '%Y-%m-%dT%H:%M:%SZ')

            # Convert the end datetime to a python value or set it to None if it doesn't exist
            if a["end_at"] == None or a["end_at"] == "":
                tournament_end_datetime = None
            else:
                tournament_end_datetime = datetime.strptime(a["end_at"], '%Y-%m-%dT%H:%M:%SZ')

            # the api doesn't always have the name field populated - this function uses the slug field if that's the case
            if a["name"] == None or a["name"] == "":
                tournament_name = a["slug"]
            else:
                tournament_name = a["name"]

            # The matches data for the tournament is saved to a variable for later use
            match_data_saved = get_match_data_by_tournament_id(a["id"])

            # tournament dict created with tournament level detail
            tournament_dict = {
                "tournament_id": a["id"],
                "tournament_name": tournament_name,
                "tournament_url": tournaments_data[2],
                "tournament_start_datetime": tournament_start_datetime,
                "tournament_end_datetime": tournament_end_datetime,
                "tournament_videogame": a["videogame"]["name"],
                "matches": match_data_saved[0]
            }

            tournaments.append(tournament_dict)
        except:
            pass
    return tournaments, tournaments_data[1], tournaments_data[2]

def get_new_API_data_by_videogame(game_id):
    # PUBG 20
    # Overwatch 14
    # Dota 2 4
    # CS:GO 3
    # LoL 1

    #variables
    url_base = "https://api.pandascore.co/"

    series_endpoint = "videogames/" + str(game_id) + "/series.json?"

    # lambda functions so the urls can be recalculated if an endpoint changes
    series_data_url = url_base + series_endpoint

    series_data = get_data(series_data_url) # series data will not have to be recalculated at anypoint

    # initialise the series array - this will hold the data the function returns
    series = []

    # save the current time to avoid this function being called multiple times and errors occuring
    time_now = datetime.now()

    # Loop through the series' fetched by the get_data function above
    for i in series_data[0]:
        # Try statement to ensure some bad data does not end the process - need to handle exceptions though
        try:
            # Convert the begin datetime to a python datetime so calculations can be done on it
            series_start_datetime = datetime.strptime(i["begin_at"], '%Y-%m-%dT%H:%M:%SZ')

            # Convert the end datetime to a python value or set it to None if it doesn't exist
            if i["end_at"] == None or i["end_at"] == "":
                series_end_datetime = None
            else:
                series_end_datetime = datetime.strptime(i["end_at"], '%Y-%m-%dT%H:%M:%SZ')

            # Only consider series' where the start date is later than the current datetime (only upcoming series)
            if series_start_datetime >= time_now or (series_end_datetime >= time_now) if series_end_datetime != None else False:

                # the api doesn't always have the name field populated - this function uses the slug field if that's the case
                if i["name"] == None or i["name"] == "":
                    series_name = i["slug"]
                    if i["slug"][:18] == "league-of-legends-":
                        series_name = i["slug"][18:]
                else:
                    series_name = i["name"]

                # Convert the modified datetime to a python value or set it to None if it doesn't exist
                if i["modified_at"] == None or i["modified_at"] =="":
                    series_modified_datetime = None
                else:
                    series_modified_datetime = datetime.strptime(i["modified_at"], '%Y-%m-%dT%H:%M:%SZ')

                # get the tournament data for the series currently in the loop so we don't fetch the data twice in the same loop
                tournament_data_saved = get_new_tournament_data_by_series_id(i["id"])

                # start create the dictionary with the series level data
                series_dict = {
                    "series_id": i["id"], # API series_id
                    "series_name": series_name, # Series name based on the function above
                    "series_url": tournament_data_saved[2],  # url containing tournament data for series (without key)
                    "series_start_datetime": series_start_datetime,
                    "series_end_datetime": series_end_datetime,
                    "series_videogame": i["videogame"]["name"],
                    "series_modified_datetime": series_modified_datetime,
                    "tournaments": tournament_data_saved[0]
                }

                series.append(series_dict)

                # reset the tournaments endpoint for additional loops
                tournaments_endpoint = "series/%s/tournaments.json?"
        except:
            pass
    return (series)

def get_all_API_data_by_videogame(game_id):
    # PUBG 20
    # Overwatch 14
    # Dota 2 4
    # CS:GO 3
    # LoL 1

    #variables
    url_base = "https://api.pandascore.co/"

    series_endpoint = "videogames/" + str(game_id) + "/series.json?"

    # lambda functions so the urls can be recalculated if an endpoint changes
    series_data_url = url_base + series_endpoint

    series_data = get_data(series_data_url) # series data will not have to be recalculated at anypoint

    # initialise the series array - this will hold the data the function returns
    series = []

    # save the current time to avoid this function being called multiple times and errors occuring
    time_now = datetime.now()

    # save all tournaments to a variable
    tournaments = Tournament.objects.all()

    tournament_ids = []
    for tournament in tournaments:
        if tournament.status != tournament.finished:
            tournament_ids.append(tournament.api_series_id)

    # Loop through the series' fetched by the get_data function above
    for i in series_data[0]:
        # Try statement to ensure some bad data does not end the process - need to handle exceptions though
        try:
            if i["id"] in tournament_ids:
                # Convert the begin datetime to a python datetime so calculations can be done on it
                series_start_datetime = datetime.strptime(i["begin_at"], '%Y-%m-%dT%H:%M:%SZ')

                # Convert the end datetime to a python value or set it to None if it doesn't exist
                if i["end_at"] == None or i["end_at"] == "":
                    series_end_datetime = None
                else:
                    series_end_datetime = datetime.strptime(i["end_at"], '%Y-%m-%dT%H:%M:%SZ')

                # the api doesn't always have the name field populated - this function uses the slug field if that's the case
                if i["name"] == None or i["name"] == "":
                    series_name = i["slug"]

                else:
                    series_name = i["name"]

                # Convert the modified datetime to a python value or set it to None if it doesn't exist
                if i["modified_at"] == None or i["modified_at"] =="":
                    series_modified_datetime = None
                else:
                    series_modified_datetime = datetime.strptime(i["modified_at"], '%Y-%m-%dT%H:%M:%SZ')

                # get the tournament data for the series currently in the loop so we don't fetch the data twice in the same loop
                tournament_data_saved = get_all_tournament_data_by_series_id(i["id"])

                # start create the dictionary with the series level data
                series_dict = {
                    "series_id": i["id"], # API series_id
                    "series_name": series_name, # Series name based on the function above
                    "series_url": tournament_data_saved[2],  # url containing tournament data for series (without key)
                    "series_start_datetime": series_start_datetime,
                    "series_end_datetime": series_end_datetime,
                    "series_videogame": i["videogame"]["name"],
                    "series_modified_datetime": series_modified_datetime,
                    "tournaments": tournament_data_saved[0]
                }

                series.append(series_dict)

                # reset the tournaments endpoint for additional loops
                tournaments_endpoint = "series/%s/tournaments.json?"
        except:
            pass
    return (series)

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
    print("working")
    for tournament in data:

        if tournament["series_videogame"] == None or tournament["series_videogame"] == "":
            videogame = None
        else:
            videogame, vcreated = Videogame.objects.get_or_create(
                videogame_name=(tournament["series_videogame"]).lower(),
                defaults={
                    "api_videogame_id": game_id
                }
            )

        t1, created = Tournament.objects.get_or_create(
            api_series_id=tournament["series_id"],
            defaults={
                "tournament_name": tournament["series_name"],
                "tournament_start_date": tournament["series_start_datetime"],
                "tournament_end_date": tournament["series_end_datetime"],
                "api_modified_at": tournament["series_modified_datetime"],
                "videogame": videogame
            }
        )
        for stage in tournament["tournaments"]:

            s1 , stage_created = Stage.objects.get_or_create(
                api_tournament_id=stage["tournament_id"],
                api_series_id=tournament["series_id"],
                defaults={
                    "stage_name": stage["tournament_name"],
                    "stage_start_date": stage["tournament_start_datetime"],
                    "stage_end_date": stage["tournament_end_datetime"],
                    "tournament": t1
                }
            )

            for match in stage["matches"]:
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
                        "api_modified_at": match["match_modified_datetime"],
                        "team_a": team_a,
                        "team_b": team_b,
                        "videogame": videogame,
                        "tournament": t1,
                        "stage": s1,
                        "game_date": match["match_start_datetime"],
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
    api_series = get_all_API_data_by_videogame(1)
    #iterate throught each tournament in the database
    print("data got")
    print(api_series)

    for tournament in tournaments:

        print(str(tournament.tournament_name) + " is now updating")

        #if the tournament is finished we don't want to be pinging the API for changes
        if tournament.status != tournament.finished:
            print("    Tournament is not finished")

            # data is fetched for each tournament from the API based on the API tournament ID

            for series in api_series:
                if series["series_id"] == tournament.api_series_id:

                    if series["series_videogame"] == None or series["series_videogame"] == "":
                        videogame = None
                    else:
                        videogame, vcreated = Videogame.objects.get_or_create(
                            videogame_name=(series["series_videogame"]).lower(),
                            defaults={
                                "api_videogame_id": 1
                            }
                        )

                    print("seies match", videogame)
                    #changes to tournament
                    tournament.tournament_start_date = series["series_start_datetime"]
                    tournament.tournament_end_date = series["series_end_datetime"]
                    tournament.api_modified_at = series["series_modified_datetime"]
                    tournament.videogame = videogame
                    tournament.save()

                    stages = Stage.objects.filter(tournament__api_series_id=tournament.api_series_id)

                    for stage in stages:
                        api_tournaments = series["tournaments"]
                        for api_tournament in api_tournaments:
                            if api_tournament["tournament_id"] == stage.api_tournament_id:

                                # changes to stage
                                stage.stage_start_date = api_tournament["tournament_start_datetime"]
                                stage.stage_end_date = api_tournament["tournament_end_datetime"]
                                stage.save()

                                print("tournament match")


                                games = Game.objects.filter(stage__api_tournament_id=stage.api_tournament_id)
                                api_games = api_tournament["matches"]
                                database_games = []
                                for game in games:
                                    database_games.append(game.api_match_id)
                                    for api_game in api_games:
                                        if api_game["match_id"] == game.api_match_id:
                                            print("match match")
                                            # changes to game

                                            #if the team id is the same then make changes else get or create the new team
                                            if game.team_a.api_team_id == api_game["team_a_id"]:
                                                game.team_a.name = api_game["team_a"]
                                                if game.team_a.picture_url != api_game["team_a_img_url"]:
                                                    try:
                                                        result = urllib_request.urlretrieve(api_game["team_a_img_url"])
                                                        game.team_a.picture.save(
                                                            os.path.basename(api_game["team_a_img_url"]),
                                                            File(open(result[0], "rb"))
                                                        )
                                                        game.team_a.save()
                                                    except:
                                                        pass
                                                    try:
                                                        game.team_a.colour = get_colors(
                                                            os.path.join(settings.MEDIA_ROOT, str(game.team_a.picture)))
                                                    except:
                                                        pass
                                                game.team_a.save()
                                            else:
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
                                                        team_a.colour = get_colors(
                                                            os.path.join(settings.MEDIA_ROOT, str(team_a.picture)))
                                                        team_a.save()
                                                    except:
                                                        pass
                                                game.team_a = team_a
                                                game.save()
                                            # team_b
                                            if game.team_b.api_team_id == api_game["team_b_id"]:
                                                game.team_b.name = api_game["team_b"]
                                                if game.team_b.picture_url != api_game["team_b_img_url"]:
                                                    try:
                                                        result = urllib_request.urlretrieve(api_game["team_b_img_url"])
                                                        game.team_b.picture.save(
                                                            os.path.basename(api_game["team_b_img_url"]),
                                                            File(open(result[0], "rb"))
                                                        )
                                                        game.team_b.save()
                                                    except:
                                                        pass
                                                    try:
                                                        game.team_b.colour = get_colors(
                                                            os.path.join(settings.MEDIA_ROOT, str(game.team_b.picture)))
                                                    except:
                                                        pass
                                                game.team_b.save()
                                            else:
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
                                                        team_b.colour = get_colors(
                                                            os.path.join(settings.MEDIA_ROOT, str(team_b.picture)))
                                                        team_b.save()
                                                    except:
                                                        pass
                                                game.team_b = team_b
                                                game.save()

                                            game.api_modified_at = api_game["match_modified_datetime"]
                                            game.videogame = videogame
                                            game.game_date =  api_game["match_start_datetime"]
                                            game.status = api_game["match_status"]
                                            game.winning_team = api_game["winner"]
                                            game.save()

                                print(database_games)
                                for api_game in api_games:
                                    if api_game["match_id"] not in database_games:
                                        print("found game not in database ", api_game["match_id"])
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
                                                team_a.colour = get_colors(
                                                    os.path.join(settings.MEDIA_ROOT, str(team_a.picture)))
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
                                                team_b.colour = get_colors(
                                                    os.path.join(settings.MEDIA_ROOT, str(team_b.picture)))
                                                team_b.save()
                                            except:
                                                pass
                                        else:
                                            # update image if image doesn't exist or image has been updated?
                                            pass

                                        m1, match_created = Game.objects.get_or_create(
                                            api_match_id=api_game["match_id"],
                                            defaults={
                                                "api_modified_at": api_game["match_modified_datetime"],
                                                "team_a": team_a,
                                                "team_b": team_b,
                                                "videogame": series["series_videogame"],
                                                "tournament": tournament,
                                                "stage": stage,
                                                "game_date": api_game["match_start_datetime"],
                                                "status": api_game["match_status"],
                                                "winning_team": api_game["winner"]
                                            }
                                        )