from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect


# Create your views here.

User = get_user_model()
from .models import Profile
from .forms import ProfileForm

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    qs = user.bet_set.all().order_by('-created')[:5]
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProfileForm(request.POST, request.FILES)
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

        # if a GET (or any other method) we'll create a blank form
    else:
        form = ProfileForm()

    context = {
        "profile":profile,
        "form":form,
        "qs":qs,
    }
    return render(request, "profiles/profile_view.html", context)

def profile_list_view(request):
    model = User.objects.all()
    context = {
        "model":model
    }
    return render(request, "profiles/profile_list.html", context)
