from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from userbetting.models import Game, BettingGameGroup, Tournament, Videogame
from .models import CommunityGroup
from profiles.models import Wallet, Profile
from django.db.models import Q
from django.http import Http404
from datetime import datetime
from datetime import timedelta
from .forms import CreateGroupForm, UpdateGroupOptionsForm, InviteMembersForm, AcceptInviteForm, JoinGroupForm
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
    invites = wallets.filter(
        Q(status=Wallet.sent)
    )
    print("ys")
    print(admin_wallets)
    form = AcceptInviteForm(request.POST or None)
    if request.method == "POST":
        print(request.POST)
        if form.is_valid():
            print(request.POST)
            wallet_id = form.cleaned_data['wallet_id']
            accept_invite = form.cleaned_data['accept_invite']
            wallet = get_object_or_404(Wallet,id=wallet_id)
            if wallet.profile == user.profile:
                if wallet.status == wallet.sent:
                    if accept_invite:
                        wallet.status = wallet.active
                    else:
                        wallet.status = wallet.declined
                    wallet.save()
                else:
                    form.add_error(None, "This invite is not active.")
            else:
                form.add_error(None, "You are not the owner of this invite.")

        else:
            print("form not valid")
    context = {
        "wallets": wallets,
        "admin_wallets": admin_wallets,
        "invites": invites,
        "form": form
    }
    return render(request, 'community/community_home.html', context)

def communitySearch(request):
    user = get_object_or_404(User, username=request.user)

    user_groups = user.profile.groups.all()

    groups = CommunityGroup.objects.all().exclude(community_id__in=user_groups).order_by('private')
    wallets = user.profile.wallets_profile.all()
    print("ys")
    form = JoinGroupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            group_id = form.cleaned_data['group_id']

            group = get_object_or_404(CommunityGroup, community_id=group_id)


            wallet, wallet_created = Wallet.objects.get_or_create(
                profile=user.profile,
                group=group,
                defaults={
                    "status": Wallet.deactivated
                }
            )
            if wallet_created:
                if group.private:
                    # ask for invite
                    wallet.status = wallet.requesting_invite
                    messages.success(request, 'Invite requested')
                else:
                    wallet.status = wallet.active
                    messages.success(request, 'Successfully joined group.')
            else:
                if wallet.status == wallet.active:
                    form.add_error(None, "You are already a member of this group.")
                else:
                    if group.private:
                        # ask for invite
                        if wallet.status == wallet.requesting_invite:
                            form.add_error(None, "You have already requested an invite from this group.")
                        else:
                            wallet.status = wallet.requesting_invite
                            messages.success(request, 'Invite requested')
                    else:
                        wallet.status = wallet.active
                        messages.success(request, 'Successfully joined group.')
            wallet.save()
    print(user_groups)
    context = {
        "model": groups,
        "form": form,
        "wallets": wallets
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

    model_array = []
    model = User.objects.all()

    group_invites = group.wallets_group.all()

    if group not in user.profile.groups.all():
        raise Http404('Page not found')

    if request.method == "POST":
        if form.is_valid():
            invitee_id = form.cleaned_data['profile_id']

            invitee_profile = get_object_or_404(Profile, id=invitee_id)
            invite, invite_created = Wallet.objects.get_or_create(
                profile=invitee_profile,
                group=group,
                defaults={
                    "status": Wallet.sent,
                    "inviter": user.profile
                }
            )
            if invite_created:
                messages.success(request, 'Form submission successful')
            else:
                if invite.status == invite.sent:
                    form.add_error(None, "This user already has a pending invite")
                elif invite.status == invite.active:
                    form.add_error(None, "This user is already a member")
                elif invite.status == invite.declined_blocked:
                    form.add_error(None, "This user is blocking invites from this group")
                else:
                    invite.status = invite.sent
                    invite.inviter = user.profile
                    invite.save()
                    messages.success(request, 'Form submission successful')
    for user_obj in model:
        invite_count = 0
        for user_invite in user_obj.profile.wallets_profile.all():
            if user_invite in group_invites:
                invite_count += 1
                if user_invite.status == user_invite.sent:
                    model_array.append({"user": user_obj, "invite_status": "sent"})
                elif user_invite.status == user_invite.active:
                    model_array.append({"user": user_obj, "invite_status": "member"})
                elif user_invite.status == user_invite.declined_blocked:
                    model_array.append({"user": user_obj, "invite_status": "blocked"})
                else:
                    model_array.append({"user": user_obj, "invite_status": "invite"})
        if invite_count == 0:
            model_array.append({"user": user_obj, "invite_status": "invite"})
    SORT_ORDER = {"member": 0, "sent": 1, "invite": 2, "blocked": 3}

    model_array = sorted(model_array, key=lambda k: SORT_ORDER[k['invite_status']])

    context = {
        "group": group,
        "model": model,
        "form": form,
        "model_array": model_array
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