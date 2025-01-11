import asyncio
from asgiref.sync import sync_to_async
from .models import PongGame, RPSGame
from user.models import Users

fps = 40

class PongGameManager:
	def __init__(self):
		self.players_connection = {
			"player1": "off",
			"player2": "off",
		}
		self.players_intra = {
			"player1": "",
			"player2": "",
		}
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

		self.win_condition = 10
		self.status = "waiting"

	async def update_game_state(self):
		while self.check_end() == False:
			if self.check_connection() == False:
				await asyncio.sleep(1)
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

			await asyncio.sleep(1/fps)
		await self.finish_game()
		await asyncio.sleep(1)
		self.status = "saved"



	def check_end(self):
		if self.scores[0] < self.win_condition and self.scores[1] < self.win_condition:
			return False
		else:
			return True

	def check_connection(self):
		if self.players_connection["player1"] == "off" or self.players_connection["player2"] == "off":
			self.status = "disconnected"
			return False
		else:
			return True

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
		self.status = "playing"
		asyncio.create_task(self.update_game_state())


	async def finish_game(self):
		status = "finished"
		if self.status == "disconnected":
			if self.players_connection["player1"] == "on":
				self.scores[0] = self.win_condition
				self.scores[1] = 0
			elif self.players_connection["player2"] == "on":
				self.scores[0] = 0
				self.scores[1] = self.win_condition
			status = self.status
		else:
			self.status = "saving"

		if self.scores[0] > self.scores[1]:
			winner_intra = self.players_intra["player1"]
			loser_intra = self.players_intra["player2"]
		else:
			loser_intra = self.players_intra["player1"]
			winner_intra = self.players_intra["player2"]

		winner = await sync_to_async(Users.objects.get)(intra_id=winner_intra)
		loser = await sync_to_async(Users.objects.get)(intra_id=loser_intra)

		game = await sync_to_async(PongGame.objects.create)(
			status=status,
			winner=winner,
			loser=loser,
			winner_score=max(self.scores[0], self.scores[1]),
			loser_score=min(self.scores[0], self.scores[1]),
			)
		winner.pong_win += 1
		loser.pong_lose += 1
		await sync_to_async(winner.save)()
		await sync_to_async(loser.save)()
		await sync_to_async(game.save)()
		self.status = "saved"


class RPSGameManager:
	def __init__(self):
		self.connection = {}
		self.intra_id = {}
		self.choice = {}
		self.result = {}
		self.status = "waiting"

	async def save_choice(self, player, choice):
		print(f"saved {player}'s choice: {choice}")
		self.choice[player] = choice
		if len(self.choice) == 2:
			self.calculate_result()
			await self.change_status("saving")
			await self.finish_game()

	def get_state(self):
		return {
			"status": self.status,
			"result": self.result,
			"choice": self.choice,
		}

	async def change_status(self, new_status):
		async with asyncio.Lock():
			print(f"status change: {self.status} -> {new_status}")
			self.status = new_status


	def calculate_result(self):
		self.result["player1"] = "win"
		self.result["player2"] = "lose"
		if self.choice["player1"] == self.choice["player2"]:
			self.result["player1"] = "draw"
			self.result["player2"] = "draw"
		elif self.choice["player1"] == "rock" and self.choice["player2"] == "paper":
			self.result["player1"] = "lose"
			self.result["player2"] = "win"
		elif self.choice["player1"] == "paper" and self.choice["player2"] == "scissors":
			self.result["player1"] = "lose"
			self.result["player2"] = "win"
		elif self.choice["player1"] == "scissors" and self.choice["player2"] == "rock":
			self.result["player1"] = "lose"
			self.result["player2"] = "win"


	async def finish_game(self):
		player1 = await sync_to_async(Users.objects.get)(intra_id=self.intra_id["player1"])
		player2 = await sync_to_async(Users.objects.get)(intra_id=self.intra_id["player2"])

		result = f"player1 {self.result['player1']}, player2 {self.result['player2']}"

		game = await sync_to_async(RPSGame.objects.create)(
			status="finished",
			result=result,
			player1 = player1,
			player2 = player2,
			player1_choice = self.choice["player1"],
			player2_choice = self.choice["player2"]
			)

		if self.result["player1"] == "win":
			player1.rps_win += 1
			player2.rps_lose += 1
		elif self.result["player1"] == "lose":
			player1.rps_lose += 1
			player2.rps_win += 1
		elif self.result["player1"] == "draw":
			player1.rps_draw += 1
			player2.rps_draw += 1

		await sync_to_async(player1.save)()
		await sync_to_async(player2.save)()
		await sync_to_async(game.save)()
		self.change_status("saved")
