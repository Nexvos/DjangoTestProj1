from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect


# Create your views here.

User = get_user_model()
from .models import Profile
from userbetting.models import Bet, Game
from .forms import ProfileForm, AddFundsForm
from django.db.models import Q

def profile_view(request):
    user = get_object_or_404(User, username=request.user)
    profile, created = Profile.objects.get_or_create(user=user)
    qs = user.user_bets.all()
    qs_active = qs.filter(Q(game__status=Game.not_begun)|Q(game__status=Game.starting)|Q(game__status=Game.ongoing)).order_by('-game__game_date')
    qs_awaiting_validation = qs.filter(Q(game__status=Game.finished_not_confirmed) | Q(game__status=Game.finished_confirmed), Q(status=Bet.open)).order_by('-game__game_date')
    qs_settled = qs.filter(Q(status=Bet.lost) | Q(status=Bet.paid)).order_by('-game__game_date')


    # 1 Queryset for active bets - I.e. Bets for games that have a status of "not_begun", "starting", "ongoing"
    # 2 Queryset for bets awaiting validation - I.e. Bts for games that have a status of "finished_not_confirmed" or "finished_confirmed" and bet status = "open"
    # 3 Queryset for settled bets - I.e. bets with a status of paid or "paid" or "lost"
    if request.method == 'POST':
        print(request.POST)
        if 'update_details' in request.POST:
            form = ProfileForm(request.POST, request.FILES)
            print(request.POST, request.FILES)
            # check whether it's valid:
            if form.is_valid():
                location = form.cleaned_data['location']
                picture = form.cleaned_data['picture']
                colour = form.cleaned_data['colour']

                profile.location = location
                profile.picture = picture
                profile.colour = colour

                profile.save()

                return HttpResponseRedirect('')

        elif 'add_funds' in request.POST:
            form = AddFundsForm(request.POST)
            print(request.POST)
            # check whether it's valid:
            if form.is_valid():
                print("valid")
                amount = form.cleaned_data['amount']
                profile.withdrawable_bank += amount

                profile.save()

                return HttpResponseRedirect('')
    else:
        form = ProfileForm()

    context = {
        "profile":profile,
        "form":form,
        "qs_active":qs_active,
        "qs_awaiting_validation": qs_awaiting_validation,
        "qs_settled":qs_settled,
    }
    return render(request, "profiles/profile_view.html", context)

def profile_public(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    qs = user.user_bets.all().order_by('game__game_date')
    qs = qs.exclude(game__status='finished_confirmed')

    context = {
        "profile":profile,
        "qs":qs,
    }
    return render(request, "profiles/profile_public.html", context)

def profile_list_view(request):
    model = User.objects.all()
    context = {
        "model": model,
    }
    return render(request, "profiles/profile_list.html", context)

def profile_add_funds(request):
    model = User.objects.all()
    context = {
        "model":model
    }
    return render(request, "profiles/profile_add_funds.html", context)
