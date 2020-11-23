import json
from rest_framework import status
from rest_framework.test import APITestCase
from levelupapi.models import GameType, Game

class GameTests(APITestCase):
    def setUp(self):
        """
        Create a new account and create sample category
        """

        # register a user
        url = "/register"
        data = {
            "username": "jweckert17",
            "password": "hunter2",
            "email": "jweckert17@gmail.com",
            "address": "123 Main Street",
            "phone_number": "555-5555",
            "first_name": "Jacob",
            "last_name": "Eckert",
            "bio": "Just a hardcore gamer 1337!"
        }
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        # store token for future tests
        self.token = json_response['token']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # store a gametype in database for future tests
        gametype = GameType()
        gametype.name = "Board game"
        gametype.save()

    def test_create_game(self):
        """
        Ensure we can create a new game
        """
        url = "/games"
        data = {
            "gameTypeId": 1,
            "skillLevel": 5,
            "name": "Clue",
            "numPlayers": 5
        }

        # set HTTP Authorization header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Make POST request to url with data object
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        # ensure you got a HTTP 201 response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ensure that properties on the created resource are all accurate
        self.assertEqual(json_response['name'], 'Clue')
        self.assertEqual(json_response['skill_level'], 5)
        self.assertEqual(json_response['num_players'], 5)

        # get the object from the db and verify that everything saved properly
        game = Game.objects.get(name="Clue")
        self.assertEqual(game.name, 'Clue')
        self.assertEqual(game.game_type.id, 1)
        self.assertEqual(game.skill_level, 5)
        self.assertEqual(game.num_players, 5)
        self.assertEqual(game.creator.id, 1)