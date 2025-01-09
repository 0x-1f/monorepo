from django.db import models
from django.utils.timezone import now

from user.models import Users

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# class Users(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     intra_id = models.CharField(max_length=255, unique=True)
#     refresh_token = models.CharField(max_length=255, default="")
#     register_date = models.DateTimeField(default=now)
#     last_login = models.DateTimeField(null=True, blank=True)
#     pong_win = models.PositiveIntegerField(default=0)
#     pong_lose = models.PositiveIntegerField(default=0)
#     tournament_win = models.PositiveIntegerField(default=0)
#     rsp_win = models.PositiveIntegerField(default=0)
#     rsp_lose = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return f"User {self.intra_id}({self.user_id})"

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
