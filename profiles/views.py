from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

# Create your views here.

User = get_user_model()
from .models import Profile

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        "profile":profile,
    }
    return render(request, "profiles/profile_view.html", context)

def profile_list_view(request):
    model = User.objects.all()
    context = {
        "model":model
    }
    return render(request, "profiles/profile_list.html", context)
