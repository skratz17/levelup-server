"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from levelupapi.models import GameType

class GameTypes(ViewSet):
    """Level up game types"""

    def retrieve(self, request, pk=None):
        """Handle GET requests for a single game type

        Returns:
            Response -- JSON serialized game type
        """
        try:
            game_type = GameType.objects.get(pk=pk)
            serializer = GameTypeSerializer(game_type, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to get al game types

        Returns:
            Response -- JSON serialized list of game types
        """
        gametypes = GameType.objects.all()

        # many=True kwarg is necessary if serializing a list of objects instead of single object
        serializer = GameTypeSerializer(gametypes, many=True, context={'request': request})
        return Response(serializer.data)

class GameTypeSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for game types"""

    class Meta:
        model = GameType
        url = serializers.HyperlinkedIdentityField(
            view_name='gametype',
            lookup_field='id'
        )
        fields = ('id', 'url', 'name')