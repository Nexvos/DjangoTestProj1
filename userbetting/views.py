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


# Create your views here.
def index(request):
    latest_game_list = Game.objects.all()
    tournament_list = Tournament.objects.all()
    # Nd to create separate qurysets for different tournament statuses and only display active tournaments
    # & tournaments not yet begun
    query = request.GET.get('q')
    current_datetime = datetime.now()
    three_months = timedelta(days=90)
    print(request.GET.get('q'))
    print(request.GET.get('activepage'))
    if query:
        latest_game_list = latest_game_list.filter(
            ~Q(status=Game.finished),
            ~Q(status=Game.finished_not_confirmed),
            ~Q(status=Game.finished_confirmed),
            ~Q(status=Game.finished_paid),
            Q(videogame__videogame_name__iexact=query)
        ).order_by('game_date')[:12]
        tournament_list = tournament_list.filter(videogame__videogame_name__iexact=query)
    else:
        latest_game_list = latest_game_list.filter(
            ~Q(status=Game.finished),
            ~Q(status=Game.finished_not_confirmed),
            ~Q(status=Game.finished_confirmed),
            ~Q(status=Game.finished_paid)
        ).order_by('game_date')[:12]
        query = False


    upcoming_tournaments = tournament_list.filter(
            Q(tournament_start_date__gt=current_datetime),
            Q(tournament_start_date__lt=current_datetime + three_months)
        ).order_by('tournament_start_date')

    ongoing_tournaments = tournament_list.filter(
            Q(tournament_start_date__lt=current_datetime),
            Q(tournament_end_date__gt=current_datetime)
        ).order_by('tournament_start_date')[:8]

    completed_tournaments = tournament_list.filter(
            Q(tournament_start_date__lt=current_datetime),
            Q(tournament_end_date__lt=current_datetime),
            Q(tournament_end_date__gt=current_datetime - three_months)
        ).order_by('tournament_start_date')

    context = {
        'latest_game_list': latest_game_list,
        'upcoming_tournaments': upcoming_tournaments,
        'ongoing_tournaments': ongoing_tournaments,
        'completed_tournaments': completed_tournaments,
        'query': query
    }
    return render(request, 'userbetting/index.html', context)

def lazy_load_games(request):
  page = request.POST.get('page')[:12]
  print(page)
  latest_game_list = Game.objects.all() # get just 5 posts
  latest_game_list = latest_game_list.filter(
      ~Q(status=Game.finished),
      ~Q(status=Game.finished_not_confirmed),
      ~Q(status=Game.finished_confirmed),
      ~Q(status=Game.finished_paid)
  ).order_by('game_date')
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
  # build a html posts list with the paginated posts
  games_list_html = loader.render_to_string(
    'userbetting/games_list.html',
    {'latest_game_list': latest_game_list}
  )
  additional_html = "<script>var loop_number=" + str(int(page) * 12 - 12) + "</script>"
  # package output data and return it as a JSON object
  output_data = {
    'games_list_html': additional_html + games_list_html,
    'has_next': games.has_next()
  }
  print(output_data)
  return JsonResponse(output_data)

def tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    tournament_games = tournament.games.all().order_by('game_date')


    context = {
        "tournament": tournament,
        "latest_game_list": tournament_games
    }
    return render(request, 'userbetting/tournament_view.html', context)

def tournament_list_view(request):
    tournament_list = Tournament.objects.all()
    activesection = request.GET.get('activesection')
    query = request.GET.get('q')
    current_datetime = datetime.now()

    if query:
        tournament_list = tournament_list.filter(videogame__videogame_name__iexact=query)
    else:
        query = 'None'

    upcoming_tournaments = tournament_list.filter(
        Q(tournament_start_date__gt=current_datetime)
    ).order_by('tournament_start_date')

    ongoing_tournaments = tournament_list.filter(
        Q(tournament_start_date__lt=current_datetime),
        Q(tournament_end_date__gt=current_datetime)
    ).order_by('tournament_start_date')

    completed_tournaments = tournament_list.filter(
        Q(tournament_start_date__lt=current_datetime),
        Q(tournament_end_date__lt=current_datetime)
    ).order_by('tournament_start_date')

    context = {
        "upcoming_tournaments": upcoming_tournaments,
        "ongoing_tournaments": ongoing_tournaments,
        "completed_tournaments": completed_tournaments,
        "activesection": activesection
    }
    return render(request, "userbetting/tournament_list_view.html", context)

def completed_game_list_view(request):
    game_list = Game.objects.all()

    query = request.GET.get('q')

    if query:
        game_list = game_list.filter(videogame__videogame_name__iexact=query)
    else:
        query = False

    completed_games = game_list.filter(
        Q(status=Game.finished) |
        Q(status=Game.finished_not_confirmed) |
        Q(status=Game.finished_confirmed) |
        Q(status=Game.finished_paid)
    ).order_by('game_date')

    context = {
        "latest_game_list": completed_games
    }
    return render(request, "userbetting/completed_game_list_view.html", context)

def testPage(request):
    print("view works")
    # update_existing_tournaments()
    update_existing_tournaments()
    context = {
    }
    return render(request, 'userbetting/test.html', context)

def detail(request, game_id):
    user = request.user
    userbets = user.user_bets.all().filter(game__game_id=game_id)
    game = get_object_or_404(Game, pk=game_id)
    qs = game.game_bets.all()

    total_bet = 0
    for bet in qs:
        total_bet += bet.amount
    context = {
        'game': game,
        'total_bet': total_bet,
        'userbets':userbets
               }
    return render(request, 'userbetting/game.html', context)