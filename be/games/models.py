from django.db import models
from user.models import Users
from django.utils.timezone import now

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

class RPSGame(models.Model):
    pong_id = models.AutoField(primary_key=True)
    creatd_date = models.DateTimeField(default=now)
    status = models.CharField(max_length=255, default="")
    result = models.CharField(max_length=255, default="")
    player1 = models.ForeignKey(Users, related_name='player1', on_delete=models.SET_NULL, null=True, blank=True)
    player2 = models.ForeignKey(Users, related_name='player2', on_delete=models.SET_NULL, null=True, blank=True)
    player1_choice = models.CharField(max_length=255, default="")
    player2_choice = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"Game {self.pong_id} ({self.status})"
