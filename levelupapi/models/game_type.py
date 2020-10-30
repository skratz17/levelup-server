"""GameType Model Module"""
from django.db import models

class GameType(models.Model):
    """GameType Database Model"""
    name = models.CharField(max_length=30)
