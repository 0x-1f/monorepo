import asyncio
from asgiref.sync import sync_to_async
from .models import PongGame, RPSGame
from user.models import Users

fps = 60

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

		self.paddle_width = 12
		self.paddle_height = 100
		self.paddle_positions = {
			"player1": (self.canvas_height - self.paddle_height) / 2,
			"player2": (self.canvas_height - self.paddle_height) / 2
			}
		self.paddle_speed = 14
		self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2}
		self.ballRadius = 10
		self.ball_speed = {"x": 5, "y": 5}

		self.win_condition = 7
		self.status = "waiting"
		self.connection = ""

	async def update_game_state(self):
		while self.check_end() == False:
			if self.check_connection() == False: # 두 플레이어 모두 지속적으로 online 상태인지 확인
				await asyncio.sleep(1)
				break
			self.ball["x"] += self.ball_speed["x"]  # 볼 스피드만큼 움직임
			self.ball["y"] += self.ball_speed["y"]  # 볼 스피드만큼 움직임

			# 천장 혹은 바닥에 닿는지 확인
			if self.ball["y"] < self.ballRadius:
				self.ball["y"] = self.ballRadius # 공위치 정정
				self.ball_speed["y"] *= -1; # 반대로 움직임
			elif self.ball["y"] > self.canvas_height - self.ballRadius:
				self.ball["y"] = self.canvas_height - self.ballRadius; # 공위치 정정
				self.ball_speed["y"] *= -1; # 반대로 움직임

			# 왼쪽 패들에 닿는지 확인
			if self.ball["x"] - self.ballRadius <= self.paddle_width:
				if self.paddle_positions["player1"] <= self.ball["y"] and self.ball["y"] <= self.paddle_positions["player1"] + self.paddle_height:
					self.ball["x"] = self.paddle_width + self.ballRadius # 공위치 정정
					self.ball_speed["x"] *= -1.1 # 반대로 움직임, 속도 증가
			elif self.ball["x"] + self.ballRadius >= self.canvas_width - self.paddle_width:
				if self.paddle_positions["player2"] <= self.ball["y"] and self.ball["y"] <= self.paddle_positions["player2"] + self.paddle_height:
					self.ball["x"] = self.canvas_width - self.paddle_width - self.ballRadius # 공위치 정정
					self.ball_speed["x"] *= -1.1 # 반대로 움직임, 속도 증가

			if self.ball_speed["y"] < 0: # 공의 방향이 위/아래 인지 확인
				ball_y_sign = -1
			else:
				ball_y_sign = 1

			# 왼쪽 벽에 닿으면 오른쪽 득점, 오른쪽 벽에 닿으면 왼쪽 득점
			if self.ball["x"] - self.ballRadius <= 0:
				self.scores[1] += 1
				self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2} #공위치 초기화
				self.ball_speed = {"x": 5, "y": 5 * ball_y_sign}  # 공의 속도 초기화, 이긴 플레이어에게 보내기
			elif self.ball["x"] + self.ballRadius >= self.canvas_width:
				self.scores[0] += 1
				self.ball= {"x": self.canvas_width / 2, "y": self.canvas_height / 2} #공위치 초기화
				self.ball_speed = {"x": -5, "y": 5 * ball_y_sign}  # 공의 속도 초기와, 이긴 플레어에게 보내기

			await asyncio.sleep(1/fps)
		await self.finish_game() # 게임 종료조건시 게임 종료 및 저장 함수 콜

	def check_end(self):  # 둘중 한명이 이기는 조건의 점수에 도달했는지 확인
		if self.scores[0] < self.win_condition and self.scores[1] < self.win_condition:
			return False
		else:
			return True

	def check_connection(self): # 둘중 한명이라도 offline 되면 disconnected 판정
		if self.players_connection["player1"] == "off" or self.players_connection["player2"] == "off":
			self.connection = "disconnected"
			return False
		else:
			return True

	async def change_status(self, new_status): # 밖에서 status 바꾸기 요청하기 위한 함수
		async with asyncio.Lock():
			self.status = new_status
		# print("status changed")

	def move_paddle(self, player, direction):  # player의 패들 이동 계산
		if direction == "up":
			self.paddle_positions[player] = max(0, self.paddle_positions[player] - self.paddle_speed)
		elif direction == "down":
			self.paddle_positions[player] = min(self.canvas_height - self.paddle_height, self.paddle_positions[player] + self.paddle_speed)

	def get_state(self): # 각 좌표, 점수, 상태 보내기
		if self.connection == "disconnected" and self.status == "saved":
			return {
				"ball": self.ball,
				"paddle_positions": self.paddle_positions,
				"left_score": self.scores[0],
				"right_score": self.scores[1],
				"status": "disconnected",
			}
		else:
			return {
				"ball": self.ball,
				"paddle_positions": self.paddle_positions,
				"left_score": self.scores[0],
				"right_score": self.scores[1],
				"status": self.status
			}

	def start_game_loop(self): # 게임 루프 시작 함수
		self.status = "playing"
		self.connection = "connected"
		asyncio.create_task(self.update_game_state())

	async def finish_game(self): # 게임 종료및 결과 저장 함수
		self.status = "saving"
		if self.connection == "disconnected": # 한명이 나가게 되면 10 대 0 부전승 처리
			self.scores[0] = 0
			self.scores[1] = 0
			if self.players_connection["player1"] == "on":
				self.scores[0] = self.win_condition
			elif self.players_connection["player2"] == "on":
				self.scores[1] = self.win_condition
			status = "disconnected"
		else:
			status = "finished"

		if self.scores[0] > self.scores[1]: # 누가 승/패 인지 판정
			winner_intra = self.players_intra["player1"]
			loser_intra = self.players_intra["player2"]
		else:
			loser_intra = self.players_intra["player1"]
			winner_intra = self.players_intra["player2"]

		winner = await sync_to_async(Users.objects.get)(intra_id=winner_intra)  # 데이터베이스에 저장하기 위해 users 객체 가져오기
		loser = await sync_to_async(Users.objects.get)(intra_id=loser_intra)  # 데이터베이스에 저장하기 위해 users 객체 가져오기

		game = await sync_to_async(PongGame.objects.create)(  # 데이터 베이스에 저장하기 위해 ponggame 객체 가져오기
			status=status,
			winner=winner,
			loser=loser,
			winner_score=max(self.scores[0], self.scores[1]),
			loser_score=min(self.scores[0], self.scores[1]),
			)
		winner.pong_win += 1
		loser.pong_lose += 1
		await sync_to_async(winner.save)()  # winner 의 user 데이터 저장
		await sync_to_async(loser.save)()  # loser 의 user 데이터 저장
		await sync_to_async(game.save)()  # PongGame 데이터 저장
		self.status = "saved"


class RPSGameManager:
	def __init__(self):
		self.connection = {}
		self.intra_id = {}
		self.choice = {}
		self.result = {}
		self.status = "waiting"

	async def save_choice(self, player, choice):  # 플레이어의 선택 저장
		async with asyncio.Lock():
			self.choice[player] = choice
			length = len(self.choice)
		if length == 2:
			await self.calculate_result()
			await self.change_status("saving")
			await self.finish_game()

	async def get_status(self):  # status 불러오기 함수
		async with asyncio.Lock():
			return self.status

	async def get_data(self):  # data 불러오기 함수
		async with asyncio.Lock():
			return {
				"status": self.status,
				"result": self.result,
				"choice": self.choice,
			}

	async def change_status(self, new_status): # 밖에서 status 바꾸기 요청하기 위한 함수
		async with asyncio.Lock():
			self.status = new_status

	async def calculate_result(self):  # 경기 결과 계산
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

	async def finish_game(self):  # 경기 끝내고 결과 저장하기
		player1 = await sync_to_async(Users.objects.get)(intra_id=self.intra_id["player1"])  # 플레이어 유저객체 가져오기
		player2 = await sync_to_async(Users.objects.get)(intra_id=self.intra_id["player2"])  # 플레이어 유저객체 가져오기

		result = f"player1 {self.result['player1']}, player2 {self.result['player2']}"

		game = await sync_to_async(RPSGame.objects.create)(  # 가위바위보 객체 가저오기
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

		await sync_to_async(player1.save)()  # 플레이어의 유저객체 저장
		await sync_to_async(player2.save)()  # 플레이어의 유저객체 저장
		await sync_to_async(game.save)()  # 가위바위보 객체 저장
		await self.change_status("saved")
