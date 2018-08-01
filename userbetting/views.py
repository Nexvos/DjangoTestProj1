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
    latest_game_list = Game.objects.order_by('game_date')
    tournament_list = Tournament.objects.all()
    # Nd to create separate qurysets for different tournament statuses and only display active tournaments
    # & tournaments not yet begun
    query = request.GET.get('q')
    current_datetime = datetime.now()
    three_months = timedelta(days=90)
    if query:
        latest_game_list = latest_game_list.filter(videogame__videogame_name__iexact=query)[:12]
        tournament_list = tournament_list.filter(videogame__videogame_name__iexact=query)
    else:
        latest_game_list = latest_game_list[:12]
        query = 'None'


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
  latest_game_list = Game.objects.order_by('game_date') # get just 5 posts
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
        "games_qs": tournament_games
    }
    return render(request, 'userbetting/tournament_view.html', context)

def tournament_list_view(request):
    tournament_list = Tournament.objects.all()

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
        "completed_tournaments": completed_tournaments
    }
    return render(request, "userbetting/tournament_list_view.html", context)

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

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))