from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .tasks import *
from profiles.tasks import *
from BettingAdmin.adminBettingFunctions import Add_new_tournament, get_colors, mark_tournaments_complete, update_existing_tournaments, get_match_data_by_tournament_id
from .models import Game, Team, Tournament
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
import os
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.http import Http404
from community.models import CommunityGroup

User = get_user_model()


# Create your views here.
def index(request, community_id=1):
    #Assuming PUBLIC is 1
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    try:
        wallet = Wallet.objects.get(group=group, profile=user.profile, status=Wallet.active)
    except Wallet.DoesNotExist:
        raise Http404('You are not a member of this group.')

    latest_game_list = BettingGameGroup.objects.filter(Q(group__community_id=community_id),
                                                       Q(status=BettingGameGroup.active)
                                                       )
    tournament_list = group.group_tournaments.all()
    test_t = Tournament.objects.get(tournament_id=89)
    print(test_t.games.all())
    # Nd to create separate qurysets for different tournament statuses and only display active tournaments
    # & tournaments not yet begun
    query = request.GET.get('q')
    current_datetime = datetime.now()
    three_months = timedelta(days=90)

    if query:
        latest_game_list = latest_game_list.filter(
            ~Q(game__status=Game.finished),
            ~Q(game__status=Game.finished_not_confirmed),
            ~Q(game__status=Game.finished_confirmed),
            ~Q(game__status=Game.finished_paid),
            Q(game__videogame__videogame_name__iexact=query)
        ).order_by('game__game_date')[:12]
        tournament_list = tournament_list.filter(videogame__videogame_name__iexact=query)

    else:
        latest_game_list = latest_game_list.filter(
            ~Q(game__status=Game.finished),
            ~Q(game__status=Game.finished_not_confirmed),
            ~Q(game__status=Game.finished_confirmed),
            ~Q(game__status=Game.finished_paid)
        ).order_by('game__game_date')[:12]
        query = "None"

    upcoming_tournaments = tournament_list.filter(
            Q(tournament_start_date__gt=current_datetime),
            Q(tournament_start_date__lt=current_datetime + three_months)
        ).order_by('tournament_start_date')

    ongoing_tournaments = tournament_list.filter(
            Q(tournament_start_date__lt=current_datetime),
            Q(tournament_end_date__gt=current_datetime)
        ).order_by('tournament_start_date')[:12]

    ongoing_tournaments1 = ongoing_tournaments[:(-(-len(ongoing_tournaments)//2))]
    ongoing_tournaments2 = ongoing_tournaments[(-(-len(ongoing_tournaments)//2)):]

    completed_tournaments = tournament_list.filter(
            Q(tournament_start_date__lt=current_datetime),
            Q(tournament_end_date__lt=current_datetime),
            Q(tournament_end_date__gt=current_datetime - three_months)
        ).order_by('tournament_start_date')
    print(latest_game_list)
    context = {
        'group': group,
        'latest_game_list': latest_game_list,
        'upcoming_tournaments': upcoming_tournaments,
        'ongoing_tournaments1': ongoing_tournaments1,
        'ongoing_tournaments2': ongoing_tournaments2,
        'completed_tournaments': completed_tournaments,
        'query': query
    }
    return render(request, 'userbetting/index.html', context)

def lazy_load_games(request, community_id=1):
  page = request.POST.get('page')[:12]
  print(page)
  group = get_object_or_404(CommunityGroup, community_id=community_id)
  latest_game_list = BettingGameGroup.objects.filter(Q(group__community_id=community_id), Q(status=BettingGameGroup.active)) # get just 5 posts
  latest_game_list = latest_game_list.filter(
      ~Q(game__status=Game.finished),
      ~Q(game__status=Game.finished_not_confirmed),
      ~Q(game__status=Game.finished_confirmed),
      ~Q(game__status=Game.finished_paid)
  ).order_by('game__game_date')
  # use Django’s pagination
  # https://docs.djangoproject.com/en/dev/topics/pagination/
  results_per_page = 12
  paginator = Paginator(latest_game_list, results_per_page)
  print(paginator.page(1).object_list)
  try:
      games = paginator.page(page)
      latest_game_list = games.object_list
  except PageNotAnInteger:
      games = paginator.page(2)
  except EmptyPage:
      games = paginator.page(paginator.num_pages)
  print("test")
  # build a html posts list with the paginated posts
  games_list_html = loader.render_to_string(
    'userbetting/games_list.html',
    {
        'latest_game_list': latest_game_list,
        'group': group,
     }
  )
  print("test2")
  additional_html = "<script>var loop_number=" + str(int(page) * 12 - 12) + "</script>"
  # package output data and return it as a JSON object
  output_data = {
    'games_list_html': additional_html + games_list_html,
    'has_next': games.has_next()
  }
  print("test")
  print(output_data)
  return JsonResponse(output_data)

def testPage(request):
    print("view works")
    # update_existing_tournaments()
    update_existing_tournaments()
    context = {
    }
    return render(request, 'userbetting/test.html', context)
