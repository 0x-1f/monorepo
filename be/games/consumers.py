import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser
import random

from .game_managers import PongGameManager, RPSGameManager
# from .models import PongGame
# from user.models import Users

fps = 40
time_limit = 5

pong_queue = []
pong_matching = 0
pong_game_rooms = {}

pong_queue_lock = asyncio.Lock()
pong_matching_lock = asyncio.Lock()

rps_queue = []
rps_matching = 0
rps_game_rooms = {}

rps_queue_lock = asyncio.Lock()
rps_matching_lock = asyncio.Lock()

class PongQueueConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global pong_queue
		# self.user = self.scope['user']  # 사용자 객체를 가져옴 (클라이언트쪽에 oauth 인증된 세션쿠키가 있다면 users객체를 받아올수 있음)
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		# if isinstance(user, AnonymousUser) or not user.is_authenticated:
        #     await self.close()  # 인증되지 않은 사용자의 연결을 거부
		# else:
		await self.accept()  # 인증된 사용자의 경우, 웹소켓 연결 수락

		async with pong_queue_lock:  # lock 걸고 큐에 사용자 추가
			pong_queue.append(self.intra_id)
		self.status = "waiting"
		self.user1_intra_id = "none"
		self.user2_intra_id = "none"
		await self.wait_for_match() # 매칭 대기

	async def disconnect(self, close_code):
		global pong_matching
		global pong_queue
		print(f"{self.intra_id} is disconnecting...")
		if self.status == "waiting":
			print("status is waiting...")
			async with pong_queue_lock:
				if self.intra_id in pong_queue:
					pong_queue.remove(self.intra_id)
					print(f"{self.intra_id} removed itself")
		elif self.intra_id == self.user1_intra_id:  # user1 인지 확인 (대기열에서 삭제는 한쪽에서만 진행)
			print(f"{self.intra_id} == {self.user1_intra_id}")
			while True:
				async with pong_matching_lock:  # 매칭에 lock 걸고 서로의 아이디를 확인했는지 확인
					if pong_matching == 2:
						print(f"pong_matchin is {pong_matching}")
						async with pong_queue_lock:  # 서로 확인했다면 lock 걸고 대기큐에서 삭제 (양쪽 모두)
							if self.user1_intra_id in pong_queue:
								print(f"{self.user1_intra_id} is in the queue")
								pong_queue.remove(self.user1_intra_id)
								print(f"{self.user1_intra_id} is removed")
							if self.user2_intra_id in pong_queue:
								print(f"{self.user2_intra_id} is in the queue")
								pong_queue.remove(self.user2_intra_id)
								print(f"{self.user2_intra_id} is removed")
							print(f"{self.intra_id} removed both")
						pong_matching = 0 # 다음 매칭을 위해 초기화
						break
					elif pong_matching == 0:
						print("pong_matching is 0")
						break
				asyncio.sleep(1) # 1초후 재확인
		print(f"{self.intra_id} is disconnected")
		await self.close()

	async def wait_for_match(self):
		global pong_queue
		global pong_matching  # 전역 변수 선언
		while True:   # 매칭 대기 루프: queue의 길이가 2 이상이면서, 나의 index가 0 or 1 이면 매칭가능
			async with pong_queue_lock:
				index = pong_queue.index(self.intra_id)
				length = len(pong_queue)
				print(f"{self.intra_id}'s index is {index} and length is {length}")
				if length > 1 and (index == 0 or index == 1):
					print(f"{self.intra_id}'s matching process on")
					self.status = "matched"
					self.user1_intra_id = pong_queue[0]
					self.user2_intra_id = pong_queue[1]

					async with pong_matching_lock:  # lock 걸고 매칭 카운트 올리기 (상대방 아이디를 확인했다는 표시)
						pong_matching += 1
					await self.send(json.dumps({"match_url": f"/ws/pong/match/{self.user1_intra_id}_{self.user2_intra_id}/"})) # intra_id 조합하여 새 웹소켓 URL 생성 및 보내기
					print(f"match_url sent to {self.intra_id}")
					break
			await asyncio.sleep(1)  # 1초 대기 후 재확인
		await self.disconnect(1000)  # 매칭후 현제 웹소켓 통신은 종료


class PongMatchConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global pong_game_rooms
		# self.user = self.scope['user'] # 사용자 ID를 가져옴 (클라이언트쪽에 oauth 인증된 세션쿠키가 있다면 users객체를 받아올수 있음)
		self.match_name = self.scope['url_route']['kwargs']['match_name']  # URL에서 게임방 이름 가져오기
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		# if isinstance(user, AnonymousUser) or not user.is_authenticated:
        #     await self.close()  # 인증되지 않은 사용자의 연결을 거부
		# else:
		await self.accept()  # 인증된 사용자의 경우, 웹소켓 연결 수락
		print(f"{self.intra_id} is ready")

		if self.match_name not in pong_game_rooms:
			pong_game_rooms[self.match_name] = PongGameManager() # 아직 생성되지 않았다면 게임방 등록 및 게임매니저 객체 생성

		player1, player2 = self.match_name.split('_')  # 방 이름으로부터 역할에 따른 아이디 저장
		async with asyncio.Lock():  # lock 걸고 내 역할을 지정 및 내 상태를 off->on 으로 활성화
			if self.intra_id == player1:
				self.role = "player1"
			elif self.intra_id == player2:
				self.role = "player2"
			pong_game_rooms[self.match_name].players_connection[self.role] = "on"
			pong_game_rooms[self.match_name].players_intra[self.role] = self.intra_id

		async with asyncio.Lock():  # 락걸고 두명 모두 on 이면 게임 시작
			if pong_game_rooms[self.match_name].players_connection["player1"] == "on" and pong_game_rooms[self.match_name].players_connection["player2"] == "on":
				pong_game_rooms[self.match_name].start_game_loop()

		self.timer = 0.0
		self.running_task = asyncio.create_task(self.send_position())


	async def disconnect(self, close_code):
		global pong_game_rooms
		async with asyncio.Lock():
			if self.match_name in pong_game_rooms and pong_game_rooms[self.match_name].players_connection[self.role] == "on":
				pong_game_rooms[self.match_name].players_connection[self.role] = "off"

		async with asyncio.Lock():
			if self.match_name in pong_game_rooms:
				if pong_game_rooms[self.match_name].players_connection["player1"] == "off" and pong_game_rooms[self.match_name].players_connection["player2"] == "off":
					del pong_game_rooms[self.match_name]

		await self.close()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if "move" in data:
			pong_game_rooms[self.match_name].move_paddle(self.role, data["move"])

	async def send_position(self):
		global pong_game_rooms
		global time_limit
		while pong_game_rooms[self.match_name].status == "waiting" and self.timer < time_limit:
			print(f"waiting for player...for {self.timer}")
			await asyncio.sleep(1/fps)
			self.timer += 1/fps
		if time_limit <= self.timer:
			pong_game_rooms[self.match_name].change_status("network_error")
		while pong_game_rooms[self.match_name].status == "playing":
			await asyncio.sleep(1/fps)
			# print("playing")
			# print(pong_game_rooms[self.match_name].status)
			await self.send(text_data=json.dumps(
				pong_game_rooms[self.match_name].get_state()
			))
		while pong_game_rooms[self.match_name].status == "saving":
			# print("saving the result...")
			await asyncio.sleep(1)
		await self.send(text_data=json.dumps(
				pong_game_rooms[self.match_name].get_state()
		))
		await self.disconnect(1000)


class RPSQueueConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global rps_queue
		# self.user = self.scope['user']  # 사용자 객체를 가져옴 (클라이언트쪽에 oauth 인증된 세션쿠키가 있다면 users객체를 받아올수 있음)
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		# if isinstance(user, AnonymousUser) or not user.is_authenticated:
        #     await self.close()  # 인증되지 않은 사용자의 연결을 거부
		# else:
		await self.accept()  # 인증된 사용자의 경우, 웹소켓 연결 수락

		async with rps_queue_lock:  # lock 걸고 큐에 사용자 추가
			rps_queue.append(self.intra_id)
		self.status = "waiting"
		self.user1_intra_id = "none"
		self.user2_intra_id = "none"
		await self.wait_for_match() # 매칭 대기

	async def disconnect(self, close_code):
		if self.status == "waiting":
			async with rps_queue_lock:
				if self.intra_id in rps_queue:
					rps_queue.remove(self.intra_id)
		elif self.intra_id == self.user1_intra_id:  # user1 인지 확인 (대기열에서 삭제는 한쪽에서만 진행)
			while True:
				async with rps_matching_lock:  # 매칭에 lock 걸고 서로의 아이디를 확인했는지 확인
					if rps_matching == 2:
						async with rps_queue_lock:  # 서로 확인했다면 lock 걸고 대기큐에서 삭제 (양쪽 모두)
							if self.user1_intra_id in rps_queue:
								rps_queue.remove(self.user1_intra_id)
							if self.user2_intra_id in rps_queue:
								rps_queue.remove(self.user2_intra_id)
						rps_matching = 0 # 다음 매칭을 위해 초기화
						await self.close()
				asyncio.sleep(1) # 1초후 재확인
		await self.close()

	async def wait_for_match(self):
		global rps_queue
		global rps_matching  # 전역 변수 선언
		while True:   # 매칭 대기 루프: queue의 길이가 2 이상이면서, 나의 index가 0 or 1 이면 매칭가능
			async with rps_queue_lock:
				index = rps_queue.index(self.intra_id)
				length = len(rps_queue)
				if length > 1 and (index == 0 or index == 1):
					self.status = "matched"
					# async with rps_queue_lock:     # lock 걸고 매칭된 intra_id 가져오기
					self.user1_intra_id = rps_queue[0]
					self.user2_intra_id = rps_queue[1]

					async with rps_matching_lock:  # lock 걸고 매칭 카운트 올리기 (상대방 아이디를 확인했다는 표시)
						rps_matching += 1
					await self.send(json.dumps({"match_url": f"/ws/rps/match/{self.user1_intra_id}_{self.user2_intra_id}/"})) # intra_id 조합하여 새 웹소켓 URL 생성 및 보내기

					break
			await asyncio.sleep(1)  # 1초 대기 후 재확인
		await self.disconnect(1000)  # 매칭후 현제 웹소켓 통신은 종료


class RPSMatchConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global rps_game_rooms
		# self.user = self.scope['user'] # 사용자 ID를 가져옴 (클라이언트쪽에 oauth 인증된 세션쿠키가 있다면 users객체를 받아올수 있음)
		self.match_name = self.scope['url_route']['kwargs']['match_name']  # URL에서 게임방 이름 가져오기
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		# if isinstance(user, AnonymousUser) or not user.is_authenticated:
        #     await self.close()  # 인증되지 않은 사용자의 연결을 거부
		# else:
		await self.accept()  # 인증된 사용자의 경우, 웹소켓 연결 수락

		if self.match_name not in rps_game_rooms:
			rps_game_rooms[self.match_name] = RPSGameManager() # 아직 생성되지 않았다면 게임방 등록 및 게임매니저 객체 생성

		player1, player2 = self.match_name.split('_')  # 방 이름으로부터 역할에 따른 아이디 저장
		async with asyncio.Lock():  # lock 걸고 내 역할을 지정 및 내 상태를 off->on 으로 활성화
			if self.intra_id == player1:
				self.role = "player1"
				self.opponent = "player2"
			elif self.intra_id == player2:
				self.role = "player2"
				self.opponent = "player1"
			rps_game_rooms[self.match_name].connection[self.role] = "on"
			rps_game_rooms[self.match_name].intra_id[self.role] = self.intra_id

		async with asyncio.Lock():  # 락걸고 두명 모두 on 이면 게임 시작
			if len(rps_game_rooms[self.match_name].connection) == 2:
				rps_game_rooms[self.match_name].status = "playing"

		self.timer = 0.0
		self.running_task = asyncio.create_task(self.send_status())


	async def disconnect(self, close_code):
		global rps_game_rooms
		async with asyncio.Lock():
			if self.role not in rps_game_rooms[self.match_name].choice:
				rps_game_rooms[self.match_name].save_choice(self.role, await self.random_RPS())

		async with asyncio.Lock():
			if self.match_name in rps_game_rooms and rps_game_rooms[self.match_name].connection[self.role] == "on":
				rps_game_rooms[self.match_name].connection[self.role] = "off"

		async with asyncio.Lock():
			if len(rps_game_rooms[self.match_name].connection) == 2:
				if rps_game_rooms[self.match_name].connection["player1"] == "off" and rps_game_rooms[self.match_name].connection["player2"] == "off":
					del rps_game_rooms[self.match_name]
			elif len(rps_game_rooms[self.match_name].connection) == 1:
				del rps_game_rooms[self.match_name]

		await self.close()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if "choice" in data:
			print("sending the choice...")
			await rps_game_rooms[self.match_name].save_choice(self.role, data["choice"])
			print("sent the choice...")


	async def send_status(self):
		global rps_game_rooms
		global time_limit
		while rps_game_rooms[self.match_name].status == "waiting" and self.timer < time_limit:
			await asyncio.sleep(1/fps)
			self.timer += 1/fps
			# print(f"{self.intra_id} is waiting ... for {self.timer}")
		if time_limit <= self.timer:
			rps_game_rooms[self.match_name].status = "network_error"
		else:
			# 시작신호 주고 5초 기다리기 (프론트에서 5초 카운트 다운)//
			await self.send(text_data=json.dumps(
				rps_game_rooms[self.match_name].get_state()
			))
			asyncio.sleep(5)

		# 두 플레이어 모두 선택을 제출했는지 확인
		while rps_game_rooms[self.match_name].status == "playing":
			await asyncio.sleep(1/fps)
			# print("playing....")

		# 결과
		while rps_game_rooms[self.match_name].status == "saving":
			await asyncio.sleep(1/fps)
		await self.send(text_data=json.dumps(
			rps_game_rooms[self.match_name].get_state()
		))
		await self.disconnect(1000)

	async def random_RPS(self):
		num = random.randint(0, 2)
		if num == 0:
			return "rock"
		elif num == 1:
			return "paper"
		elif num == 2:
			return "scissors"
