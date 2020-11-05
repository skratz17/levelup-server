"""Profile ViewSet and Serializers"""
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from levelupapi.models import Gamer, Event, Game

User = get_user_model()

class Profile(ViewSet):
    """Profiles ViewSet"""

    def list(self, request):
        """GET profile, not really a "list" but just want to be able
        to expose this info via /profile"""

        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.filter(registration__gamer=gamer)

        events = EventSerializer(events, many=True, context={'request': request})
        gamer = GamerSerializer(gamer, many=False, context={'request': request})

        profile = {}
        profile["gamer"] = gamer.data
        profile["events"] = events.data
        
        return Response(profile)

class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for gamer's related Django user"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')

class GamerSerializer(serializers.ModelSerializer):
    """JSON serializer for gamers"""
    user = UserSerializer(many=False)

    class Meta:
        model = Gamer
        fields = ('user', 'bio')

class GameSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for games"""
    class Meta:
        model = Game
        fields = ('name', )

class EventSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for events"""
    game = GameSerializer(many=False)

    class Meta:
        model = Event
        fields = ('id', 'url', 'game', 'location', 'date', 'time')
