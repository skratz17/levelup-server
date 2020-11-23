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

    def test_get_game(self):
        """
        Ensure we can get an existing game.
        """

        # Seed the DB with a game
        game = Game()
        game.game_type_id = 1
        game.skill_level = 5
        game.name = "Monopoly"
        game.num_players = 4
        game.creator_id = 1

        game.save()

        # Ensure user is authorized
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # GET the game that we just created
        response = self.client.get(f"/games/{game.id}")

        json_response = json.loads(response.content)

        # Ensure 200 status code on successful GET
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure response properties are what we expect them to be
        self.assertEqual(json_response["name"], "Monopoly")
        self.assertEqual(json_response["skill_level"], 5)
        self.assertEqual(json_response["num_players"], 4)
        self.assertEqual(json_response["creator"]["id"], 1)
        self.assertEqual(json_response["game_type"]["id"], 1)

    def test_change_game(self):
        """
        Ensure we can change an existing game
        """
        game = Game()
        game.game_type_id = 1
        game.skill_level = 3
        game.name = "Sorry"
        game.num_players = 4
        game.creator_id = 1
        game.save()

        data = {
            "gameTypeId": 1,
            "skillLevel": 2,
            "name": "Sorry!",
            "numPlayers": 4
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # PUT the new data to update the game
        response = self.client.put(f"/games/{game.id}", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # GET the game again after updating
        response = self.client.get(f"/games/{game.id}")       
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(json_response["name"], "Sorry!")
        self.assertEqual(json_response["skill_level"], 2)
        self.assertEqual(json_response["num_players"], 4)
        self.assertEqual(json_response["creator"]["id"], 1)
        self.assertEqual(json_response["game_type"]["id"], 1)

    def test_delete_game(self):
        """
        Ensure we can delete an existing game
        """
        game = Game()
        game.game_type_id = 1
        game.skill_level = 3
        game.name = "Sorry"
        game.num_players = 4
        game.creator_id = 1
        game.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Delete the game we just created and verify a 204 response
        response = self.client.delete(f"/games/{game.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to delete the same game again and verify a 404 respons
        response = self.client.delete(f"/games/{game.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)