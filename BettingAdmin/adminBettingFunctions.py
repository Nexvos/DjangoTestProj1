import requests
from datetime import datetime


# Account for pagination (read docs)

def get_future_match_data():
    url_base = "https://api.pandascore.co/"
    series_endpoint = "videogames/1/series.json?"
    tournaments_endpoint = "series/%s/tournaments.json?"
    matches_endpoint = "/tournaments/%s/matches.json?"
    optional_filter = "filter[name]=Overwatch&"
    api_key = "token=7HNKtu8m8q0haBoJfP1N-S1xGFi4Po9Xm16JQYxWcdMqtnr7IQE"

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
            datetime_object = datetime.strptime(i["begin_at"], '%Y-%m-%dT%H:%M:%SZ')
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
                        "matches": []
                    }
                    if tournament_dict["series_name"] == "":
                        tournament_dict["series_name"] = i["slug"]

                    match_dicts = []
                    matches_endpoint = matches_endpoint % a["id"]
                    for b in matches_data():
                        try:
                            match_dict = {
                                "match_id": b["id"],
                                "match_name": b["name"],
                                "match_url": matches_data_url(),
                                "match_status": b["status"],
                                "match_start_datetime": b["begin_at"]
                                "match_modified_datetime": b["modified_at"]
                                "winner": b["winner"],
                                "team_a": b["opponents"][0]["opponent"]["name"],
                                "team_b": b["opponents"][1]["opponent"]["name"],
                                "team_a_id": b["opponents"][0]["opponent"]["id"],
                                "team_b_id": b["opponents"][1]["opponent"]["id"],
                                "team_a_img_url": b["opponents"][0]["opponent"]["image_url"],
                                "team_b_img_url": b["opponents"][1]["opponent"]["image_url"]
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


def update_existing_match_data():
    pass


print(get_future_match_data())






