from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .tasks import *
from profiles.tasks import *
from BettingAdmin.adminBettingFunctions import get_colors, mark_tournaments_complete, update_existing_tournaments, get_match_data_by_tournament_id, get_tournament_data_by_series_id
from .models import Game, Team, Tournament
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
import os

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
        latest_game_list = latest_game_list.filter(videogame__iexact=query)
        tournament_list = tournament_list.filter(videogame__iexact=query)
    else:
        query = "Betting Page"


    upcoming_tournaments = tournament_list.filter(
            Q(tournament_start_date__gt=datetime.now()),
            Q(tournament_start_date__lt=datetime.now() + three_months)
        ).order_by('tournament_start_date')

    ongoing_tournamnts = tournament_list.filter(
            Q(tournament_start_date__lt=datetime.now()),
            Q(tournament_end_date__gt=datetime.now())
        ).order_by('tournament_start_date')

    completed_tournaments = tournament_list.filter(
            Q(tournament_start_date__lt=datetime.now()),
            Q(tournament_end_date__lt=datetime.now()),
            Q(tournament_end_date__gt=datetime.now() - three_months)
        ).order_by('tournament_start_date')

    context = {
        'latest_game_list': latest_game_list,
        'upcoming_tournaments': upcoming_tournaments,
        'ongoing_tournamnts': ongoing_tournamnts,
        'completed_tournaments': completed_tournaments,
        'query': query
    }
    return render(request, 'userbetting/index.html', context)

def tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    tournament_games = tournament.games.all().order_by('game_date')


    context = {
        "tournament": tournament,
        "games_qs": tournament_games
    }
    return render(request, 'userbetting/tournament_view.html', context)

def testPage(request):
    teams = Team.objects.all()
    # pay out bets function
    # pay_bets()
    print(get_tournament_data_by_series_id(1441))
    # print(os.path.join(settings.MEDIA_ROOT, str(teams[8].picture)))
    # print(get_colors(os.path.join(settings.MEDIA_ROOT, str(teams[8].picture))))
    # for team in teams:
    #     team.colour = get_colors(os.path.join(settings.MEDIA_ROOT, str(team.picture)))
    #     team.save()
    # Rank users function
    # rank_users_winnings()

    context = {
        'games':teams

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