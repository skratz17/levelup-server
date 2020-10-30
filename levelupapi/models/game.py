"""Game Model Module"""
from django.db import models

class Game(models.Model):
    """Game Database Model"""
    name = models.CharField(max_length=100)
    num_players = models.IntegerField()
    skill_level = models.IntegerField()
    creator = models.ForeignKey("Gamer", on_delete=models.CASCADE)
    game_type = models.ForeignKey("GameType", on_delete=models.CASCADE)
