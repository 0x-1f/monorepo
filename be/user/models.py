from django.db import models
from django.utils.timezone import now

class Users(models.Model):
	user_id = models.AutoField(primary_key=True)
	intra_id = models.CharField(max_length=255, unique=True)
	refresh_token = models.CharField(max_length=255, default="")
	register_date = models.DateTimeField(default=now)
	last_login = models.DateTimeField(null=True, blank=True)
	pong_win = models.PositiveIntegerField(default=0)
	pong_lose = models.PositiveIntegerField(default=0)
	tournament_win = models.PositiveIntegerField(default=0)
	rsp_win = models.PositiveIntegerField(default=0)
	rsp_lose = models.PositiveIntegerField(default=0)

	def __str__(self):
		return f"User {self.intra_id}({self.user_id})"
# Create your models here.
