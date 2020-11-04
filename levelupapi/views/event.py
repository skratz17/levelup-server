"""View module for handling requests about events"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from levelupapi.models import Game, Event, Gamer, EventGamer
from levelupapi.views.game import GameSerializer

User = get_user_model()

class Events(ViewSet):
    """Level up events"""

    def create(self, request):
        """Handle POST operations for events

        Returns
            Response -- JSON serialized event instance
        """
        creator = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data['gameId'])

        event = Event()
        event.time = request.data['time']
        event.date = request.data['date']
        event.location = request.data['location']
        event.creator = creator
        event.game = game

        try:
            event.save()
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except ValidationError as ex:
            return Response({'reason': ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({'message': 'No event with given id found.'}, status=status.HTTP_404_NOT_FOUND)
        
        event.joined = None
        try:
            EventGamer.objects.get(event=event, gamer=gamer)
            event.joined = True
        except EventGamer.DoesNotExist:
            event.joined = False

        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        creator = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data['gameId'])

        event = Event.objects.get(pk=pk)
        event.date = request.data['date']
        event.time = request.data['time']
        event.location = request.data['location']
        event.creator = creator
        event.game = game

        event.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       

    def list(self, request):
        """Handle GET requests to events resource

        Returns:
            Response -- JSON serialized list of events
        """
        events = Event.objects.all()
        gamer = Gamer.objects.get(user=request.auth.user)

        # Support filtering events by game
        game = self.request.query_params.get('gameId', None)
        if game is not None:
            events = events.filter(game__id=type)

        for event in events:
            event.joined = None

            try:
                EventGamer.objects.get(event=event, gamer=gamer)
                event.joined = True

            except EventGamer.DoesNotExist:
                event.joined = False

        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def signup(self, request, pk=None):
        """Managing gamers signing up for events"""

        # A gamer wants to sign up for an event
        if request.method == "POST":
            event = Event.objects.get(pk=pk)
            gamer = Gamer.objects.get(user=request.auth.user)

            try:
                # Determine if user is already signed up
                registration = EventGamer.objects.get(event=event, gamer=gamer)
                return Response(
                    {'message': 'Gamer already signed up for this event.'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            except EventGamer.DoesNotExist:
                # The user is not signed up
                registration = EventGamer()
                registration.event = event
                registration.gamer = gamer
                registration.save()

                return Response({}, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            # Handle the case that client specifies an event that does not exist
            try:
                event = Event.objects.get(pk=pk)
            except Event.DoesNotExist:
                return Response(
                    {'message': 'Event does not exist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            gamer = Gamer.objects.get(user=request.auth.user)

            try:
                # Try to delete the signup
                registration = EventGamer.objects.get(
                    event=event, gamer=gamer
                )
                registration.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except EventGamer.DoesNotExist:
                return Response(
                    {'message': 'Not currently registered for event.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # If user sent a request that was not POST or DELETE
        # Tell them their method is not supported
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class EventUserSerializer(serializers.ModelSerializer):
    """JSON serializer for event creator's related Django user"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class EventGamerSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer"""
    user = EventUserSerializer(many=False)
    class Meta:
        model = Gamer
        fields = ('user', )

class EventSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for events"""
    creator = EventGamerSerializer(many=False)
    game = GameSerializer(many=False)

    class Meta:
        model = Event
        url = serializers.HyperlinkedIdentityField(
            view_name='event',
            lookup_field='id'
        )
        fields = ('id', 'url', 'game', 'creator', 'location', 'date', 'time', 'joined')
