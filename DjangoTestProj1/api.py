from django.contrib.auth.models import User
from userbetting.models import Game, Team, Bet
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.


class BetSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField(many=False)
    chosen_team = serializers.StringRelatedField(many=False)

    class Meta:
        model = Bet
        fields = ('bet_id', 'user', 'chosen_team', 'amount')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    user_bets = BetSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'user_bets')

class GameSerializer(serializers.HyperlinkedModelSerializer):
    team_a = serializers.StringRelatedField(many=False)
    team_b = serializers.StringRelatedField(many=False)
    game_bets = BetSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ('game_id', 'team_a', 'team_b', 'videogame', 'game_date', 'winning_team', 'game_bets')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'games', GameViewSet)
