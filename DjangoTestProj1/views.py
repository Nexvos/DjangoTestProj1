from django.shortcuts import render
from userbetting.models import Tournament
from django.db.models import Q
from datetime import datetime
from datetime import timedelta

# Create your views here.
def home(request):
	tournament_list = Tournament.objects.all()

	three_months = timedelta(days=90)

	ongoing_tournamnts = tournament_list.filter(
		Q(tournament_start_date__lt=datetime.now()),
		Q(tournament_end_date__gt=datetime.now())
	).order_by('tournament_start_date')

	context = {
		'ongoing_tournamnts': ongoing_tournamnts
	}

	return render(request, "home.html", context)

