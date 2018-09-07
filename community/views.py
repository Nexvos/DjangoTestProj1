from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from userbetting.models import Game, BettingGameGroup, Tournament
from .models import CommunityGroup
from django.db.models import Q
from django.http import Http404
from datetime import datetime
from datetime import timedelta

User = get_user_model()

# Create your views here.
def communityHome(request):
    user = get_object_or_404(User, username=request.user)
    wallets = user.profile.wallets_profile.all()
    admin_wallets = wallets.filter(Q(admin=True))
    invites = user.profile.community_invites_profile.all()
    print("ys")
    print(admin_wallets)
    context = {
        "wallets": wallets,
        "admin_wallets": admin_wallets,
        "invites": invites
    }
    return render(request, 'community/community_home.html', context)

def communitySearch(request):
    groups = CommunityGroup.objects.all()
    print("ys")
    context = {
        "model": groups,
    }
    return render(request, 'community/search_community.html', context)

def communityCreate(request):
    user = get_object_or_404(User, username=request.user)
    wallets = user.profile.wallets_profile.all()
    admin_wallets = wallets.filter(Q(admin=True))
    invites = user.profile.community_invites_profile.all()
    print("ys")
    print(admin_wallets)
    context = {
        "wallets": wallets,
        "admin_wallets": admin_wallets,
        "invites": invites
    }
    return render(request, 'community/create_community.html', context)

def communityPage(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')



    context = {

        "group": group
    }
    return render(request, 'community/community_page.html', context)

def tournament_list_view(request, community_id=1):
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    tournament_list = group.group_tournaments.all()
    activesection = request.GET.get('activesection')
    query = request.GET.get('q')
    current_datetime = datetime.now()


    if query:
        if query !='None':
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
        "group": group,
        "upcoming_tournaments": upcoming_tournaments,
        "ongoing_tournaments": ongoing_tournaments,
        "completed_tournaments": completed_tournaments,
        "activesection": activesection
    }
    return render(request, "community/tournament_list_view.html", context)

def invitePage(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)

    model = User.objects.all()

    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group,
        "model": model
    }
    return render(request, 'community/community_invite.html', context)

def adminPageOptions(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group
    }
    return render(request, 'community/community_admin.html', context)
def adminPageTournaments(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group
    }
    return render(request, 'community/community_admin.html', context)
def adminPageAddGames(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group
    }
    return render(request, 'community/community_admin.html', context)
def adminPageEditGames(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group
    }
    return render(request, 'community/community_admin.html', context)

def adminPageMembers(request, community_id):
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    context = {
        "group": group
    }
    return render(request, 'community/community_admin.html', context)

def tournament_view(request, tournament_id, community_id=1):
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
    tournament_games = BettingGameGroup.objects.filter(
        Q(group__community_id=community_id),
        Q(game__tournament__tournament_id=tournament_id)
    ).order_by('game__game_date')

    context = {
        "group": group,
        "tournament": tournament,
        "latest_game_list": tournament_games
    }
    return render(request, 'community/tournament_view.html', context)

def completed_game_list_view(request, community_id=1):
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    game_list = BettingGameGroup.objects.filter(
        Q(group__community_id=community_id)
    ).order_by('game__game_date')

    query = request.GET.get('q')
    print(game_list)
    if query:
        if query != 'None':
            game_list = game_list.filter(
                Q(game__videogame__videogame_name__iexact=query)
            )
    else:
        query = "None"

    completed_games = game_list.filter(
        Q(game__status=Game.finished) |
        Q(game__status=Game.finished_not_confirmed) |
        Q(game__status=Game.finished_confirmed) |
        Q(game__status=Game.finished_paid)
    ).order_by('game__game_date')
    print(completed_games)
    context = {
        "group": group,
        "latest_game_list": completed_games
    }
    return render(request, "community/completed_game_list_view.html", context)

def detail(request, betting_group_id, community_id):
    user = request.user
    userbets = user.user_bets.all().filter(betting_group__betting_group_id=betting_group_id)
    game_bgg = get_object_or_404(BettingGameGroup, pk=betting_group_id)
    qs = game_bgg.game_bets.all()

    total_bet = 0
    for bet in qs:
        total_bet += bet.amount
    context = {
        'game_bgg': game_bgg,
        'total_bet': total_bet,
        'userbets':userbets
               }
    return render(request, 'community/game.html', context)