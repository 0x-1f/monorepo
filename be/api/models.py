from django.db import models
from django.utils.timezone import now

from user.models import Users

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class PongGame(models.Model):
    pong_id = models.AutoField(primary_key=True)
    creatd_date = models.DateTimeField(default=now)
    status = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=255, default="")
    winner = models.ForeignKey(Users, related_name='games_won', on_delete=models.SET_NULL, null=True, blank=True)
    loser = models.ForeignKey(Users, related_name='games_lost', on_delete=models.SET_NULL, null=True, blank=True)
    winner_score = models.PositiveIntegerField(null=True, blank=True)
    loser_score = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Game {self.pong_id} ({self.status})"

# class RSPGame(models.Model):
#     rsp_id = models.AutoField(primary_key=True)
#     creatd_date = models.DateTimeField(default=now)
#     status = models.CharField(max_length=255, default="")
#     winner = models.ForeignKey(Users, related_name='games_won', on_delete=models.SET_NULL, null=True, blank=True)
#     loser = models.ForeignKey(Users, related_name='games_lost', on_delete=models.SET_NULL, null=True, blank=True)
#     winner_choice = models.PositiveIntegerField(null=True, blank=True)
#     loser_choice = models.PositiveIntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"Game {self.rsp_id} ({self.status})"
