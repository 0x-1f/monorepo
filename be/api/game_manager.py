import asyncio

# from .models import PongGame

class GameManager:
	def __init__(self):
		self.players = {}
		self.scores = [0, 0]
		self.canvas_width = 800
		self.canvas_height = 600

		self.paddle_width = 10
		self.paddle_height = 100
		self.paddle_positions = {
			"player1": (self.canvas_height - self.paddle_height) / 2,
			"player2": (self.canvas_height - self.paddle_height) / 2
			}
		self.paddle_speed = 12
		self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2}
		self.ballRadius = 10
		self.ball_speed = {"x": 5, "y": 5}

		self.win_condition = 5
		self.status = "ready"

	async def update_game_state(self):
		while self.check_end() == False:
			if self.check_connection() == False:
				break

			# 볼 스피드만큼 움직임
			self.ball["x"] += self.ball_speed["x"]
			self.ball["y"] += self.ball_speed["y"]

			# 천장 혹은 바닥에 닿는지 확인
			if self.ball["y"] < self.ballRadius:
				self.ball["y"] = self.ballRadius # 공위치 정정
				self.ball_speed["y"] *= -1; # 반대로 움직임
			elif self.ball["y"] > self.canvas_height - self.ballRadius:
				self.ball["y"] = self.canvas_height - self.ballRadius; # 공위치 정정
				self.ball_speed["y"] *= -1; # 반대로 움직임

			# 왼쪽 벽에 닿는지 확인
			if self.ball["x"] - self.ballRadius <= 0:
				if self.paddle_positions["player1"] <= self.ball["y"] and self.ball["y"] <= self.paddle_positions["player1"] + self.paddle_height:
					self.ball["x"] = self.paddle_width + self.ballRadius # 공위치 정정
					self.ball_speed["x"] *= -1 # 반대로 움직임
				else: # 오른쪽 플레이어 득점
					self.scores[1] += 1
					self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2} #공위치 초기화

			# 오른쪽 벽에 닿는지 확인
			if self.ball["x"] + self.ballRadius >= self.canvas_width:
				if self.paddle_positions["player2"] <= self.ball["y"] and self.ball["y"] <= self.paddle_positions["player2"] + self.paddle_height:
					self.ball["x"] = self.canvas_width - self.paddle_width - self.ballRadius # 공위치 정정
					self.ball_speed["x"] *= -1 # 반대로 움직임
				else: # 오른쪽 플레이어 득점
					self.scores[0] += 1
					self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2} #공위치 초기화

			await asyncio.sleep(1/40)
		# self.finish_game()
		await asyncio.sleep(1)
		self.status = "finished"


	def check_end(self):
		if self.scores[0] < self.win_condition and self.scores[1] < self.win_condition:
			return False
		else:
			self.status = "saving"
			return True

	def check_connection(self):
		if len(self.players) == 2:
			return True
		else:
			self.status = "disconnected"
			return False

	def move_paddle(self, player, direction):
		if direction == "up":
			self.paddle_positions[player] = max(0, self.paddle_positions[player] - self.paddle_speed)
		elif direction == "down":
			self.paddle_positions[player] = min(self.canvas_height - self.paddle_height, self.paddle_positions[player] + self.paddle_speed)

	def get_state(self):
		return {
			"ball": self.ball,
			"paddle_positions": self.paddle_positions,
			"left_score": self.scores[0],
			"right_score": self.scores[1],
			"status": self.status,
		}

	def start_game_loop(self):
		asyncio.create_task(self.update_game_state())


	# def finish_game(self):
	# 	if self.status == "disconnected":
	# 		if "player1" in self.players:
	# 			self.scores[0] = self.win_condition
	# 			self.scores[1] = 0
	# 		elif "player2" in self.players:
	# 			self.scores[0] = 0
	# 			self.scores[1] = self.win_condition

	# 	if self.scores[0] > self.scores[1]:
	# 		winner = self.players[0]
	# 		loser = self.players[1]
	# 	else:
	# 		loser = self.players[0]
	# 		winner = self.players[1]

	# 	game = PongGame.objects.create(
	# 		status = self.status,
	# 		winner_id = winner,
	# 		loser_id = loser,
	# 		winner_score = max(self.scores[0], self.scores[1]),
	# 		loser_score = min(self.scores[0], self.scores[1])
	# 	)
	# 	game.save()
	# 	self.status = "finished"
