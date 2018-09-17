from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from userbetting.models import Game, BettingGameGroup, Tournament, Videogame
from .models import CommunityGroup
from profiles.models import Wallet, Profile, CommunityInvite
from django.db.models import Q
from django.http import Http404
from datetime import datetime
from datetime import timedelta
from .forms import CreateGroupForm, UpdateGroupOptionsForm, InviteMembersForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages

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
    form = CreateGroupForm()
    if request.method == "POST":

        print(request.POST)
        community_name = request.POST['community_name']
        if 'invite_only' in request.POST:
            invite_only = request.POST['invite_only']
        else:
            invite_only = False
        if 'members_can_invite' in request.POST:
            members_can_invite = request.POST['members_can_invite']
        else:
            members_can_invite = False
        header_background_colour = request.POST['header_background_colour']
        header_text_colour = request.POST['header_text_colour']
        tournaments = ""
        if 'tournaments' in request.POST:
            for t in request.POST.getlist("tournaments"):
                tournaments += (t + ",")
        daily_payout = request.POST["daily_payout"]

        form_dict = {
            "community_name": community_name,
            "invite_only": invite_only,
            "members_can_invite": members_can_invite,
            "header_background_colour": header_background_colour,
            "header_text_colour": header_text_colour,
            "tournaments": tournaments,
            "daily_payout": daily_payout
        }
        form = CreateGroupForm(form_dict)
        # check whether it's valid:
        if form.is_valid():
            print("valid")
            user = get_object_or_404(User, username=request.user)
            community_name = form.cleaned_data['community_name']
            invite_only = form.cleaned_data['invite_only']
            members_can_invite = form.cleaned_data['members_can_invite']
            header_background_colour = form.cleaned_data['header_background_colour']
            header_text_colour = form.cleaned_data['header_text_colour']
            tournaments = form.cleaned_data['tournaments']
            daily_payout = form.cleaned_data['daily_payout']

            new_group = CommunityGroup()
            new_group.name = community_name
            new_group.private = invite_only
            new_group.members_can_inv = members_can_invite
            new_group.header_background_colour = header_background_colour
            new_group.header_text_colour = header_text_colour
            new_group.daily_payout = daily_payout
            new_group.save()

            user_wallet = Wallet()
            user_wallet.profile = user.profile
            user_wallet.group = new_group
            user_wallet.withdrawable_bank = daily_payout
            user_wallet.founder = True
            user_wallet.admin = True
            user_wallet.save()

            tournament_list = tournaments.split(",")
            tournament_list_int = []
            tournament_objs = []
            print(tournament_list)
            for t in tournament_list:
                try:
                    t = int(t)
                    tournament_list_int.append(t)
                except:
                    pass
            print(tournament_list_int)
            for t in tournament_list_int:
                if isinstance(t, int):
                    tournament_to_add = get_object_or_404(Tournament, tournament_id=t)
                    tournament_to_add.groups.add(new_group)

            return redirect('community:communityPage', community_id=new_group.community_id)

    public = get_object_or_404(CommunityGroup, name="PUBLIC")
    tournaments = public.group_tournaments.all()
    videogame_list = []
    videogame_dict = []
    for tournament in tournaments:
        if tournament.videogame not in videogame_list:
            videogame_list.append(tournament.videogame)
            videogame_dict.append({"videogame": tournament.videogame, "tournaments": []})
        for dict in videogame_dict:
            if dict["videogame"] == tournament.videogame:
                dict["tournaments"].append(tournament)

    print(videogame_dict)

    context = {
        "videogame_dict": videogame_dict,
        "form": form
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
    form = InviteMembersForm(request.POST or None)

    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)

    model = User.objects.all()

    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    if request.method == "POST":
        if form.is_valid():
            invitee_id = form.cleaned_data['profile_id']

            invitee_profile = get_object_or_404(Profile, id=invitee_id)
            invite, invite_created = CommunityInvite.objects.get_or_create(
                profile=invitee_profile,
                group=group,
                defaults={
                    "status": CommunityInvite.sent,
                    "inviter": user.profile
                }
            )
            if invite_created:
                messages.success(request, 'Form submission successful')
            else:
                if invite.status == invite.sent:
                    form.add_error(None, "This user already has a pending invite")
                elif invite.status == invite.accepted:
                    form.add_error(None, "This user is already a member")
                elif invite.status == invite.declined_blocked:
                    form.add_error(None, "This user is blocking invites from this group")
                else:
                    invite.status = invite.sent
                    invite.inviter = user.profile
                    invite.save()
                    messages.success(request, 'Form submission successful')


    context = {
        "group": group,
        "model": model,
        "form": form
    }
    return render(request, 'community/community_invite.html', context)

def adminPageOptions(request, community_id):
    form = UpdateGroupOptionsForm(request.POST or None)
    user = get_object_or_404(User, username=request.user)
    group = get_object_or_404(CommunityGroup, community_id=community_id)
    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    if request.method == "POST":
        if form.is_valid():
            invite_only = form.cleaned_data['invite_only']
            members_can_invite = form.cleaned_data['members_can_invite']
            header_background_colour = form.cleaned_data['header_background_colour']
            header_text_colour = form.cleaned_data['header_text_colour']
            daily_payout = form.cleaned_data['daily_payout']

            group.private = invite_only
            group.members_can_inv = members_can_invite
            group.header_background_colour = header_background_colour
            group.header_text_colour = header_text_colour
            group.daily_payout = daily_payout
            group.save()

    context = {
        "group": group,
        "form": form
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