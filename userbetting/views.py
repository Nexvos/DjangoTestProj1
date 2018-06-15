from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import Game

# Create your views here.
def index(request):
    latest_game_list = Game.objects.order_by('game_date')
    context = {
        'latest_game_list': latest_game_list,
    }
    return render(request, 'userbetting/index.html', context)

def testPage(request):
    context = {

    }
    return render(request, 'userbetting/test.html', context)

def detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    qs = game.bet_set.all()
    total_bet = 0
    for bet in qs:
        total_bet += bet.amount
    context = {
        'game': game,
        'total_bet': total_bet
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