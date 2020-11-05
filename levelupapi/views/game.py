"""View module for handling requests about games"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from levelupapi.models import Game, GameType, Gamer

class Games(ViewSet):
    """Level up games"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized game instance
        """

        # find the related objects for the new game instance
        gamer = Gamer.objects.get(user=request.auth.user)
        game_type = GameType.objects.get(pk=request.data["gameTypeId"])

        game = Game()
        game.name = request.data["name"]
        game.num_players = request.data["numPlayers"]
        game.skill_level = request.data["skillLevel"]
        game.creator = gamer
        game.game_type = game_type

        # Try to save the new game to DB and respond with the serialized Game to client
        try:
            game.save()
            serializer = GameSerializer(game, context={'request': request})
            return Response(serializer.data)
        
        # If a validation error occured in the DB save step, respond with 400 to client
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for a single game

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            # `pk` is a parameter to this function, and Django parses it from
            # URL route parameter http://localhost:8000/games/2
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        game_type = GameType.objects.get(request.data["gameTypeId"])

        # mostly the same thing as POST, but this time update the resource w/ given pk
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response(
                {'message': 'The specified gameId does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        game.name = request.data["name"]
        game.num_players = request.data["numPlayers"]
        game.skill_level = request.data["skillLevel"]
        game.creator = gamer
        game.game_type = game_type

        game.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a game

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            game = Game.objects.get(pk=pk)
            game.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource

        Returns:
            Response -- JSON serialized list of games
        """
        games = Game.objects.all()

        # Support filtering games by type, e.g.:
        #   http://localhost:8000/games?type=1

        game_type = self.request.query_params.get('type', None)
        if game_type is not None:
            games = games.filter(game_type__id=game_type)
        
        serializer = GameSerializer(games, many=True, context={'request': request})

        return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    """JSON serialiezr for user"""
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class GamerSerializer(serializers.ModelSerializer):
    """JSON serializer for gamer"""
    user = UserSerializer(many=False)

    class Meta:
        model = Gamer
        fields = ('user', )

class GameSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for games"""
    creator = GamerSerializer(many=False)

    class Meta:
        model = Game
        url = serializers.HyperlinkedIdentityField(
            view_name='game',
            lookup_field='id'
        )
        fields = ('id', 'url', 'name', 'num_players', 'skill_level', 'creator', 'game_type')
        depth = 1
        