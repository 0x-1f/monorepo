import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import random

from .game_managers import PongGameManager, RPSGameManager

fps = 60 # 1초당 refresh 횟수
time_limit = 10 # 상대방이 안들어올때 network error 로 넘기는 시간 기준 (초)

# pong game 을 위한 대기 큐, 상호 확인, 게임 방 딕셔너리 그리고 lock
pong_queue = []
pong_cross_check = 0
pong_game_rooms = {}
pong_queue_lock = asyncio.Lock()
pong_cross_lock = asyncio.Lock()

# 가위바위보 을 위한 대기 큐, 상호 확인, 게임 방 딕셔너리 그리고 lock
rps_queue = []
rps_cross_check = 0
rps_game_rooms = {}
rps_queue_lock = asyncio.Lock()
rps_cross_check_lock = asyncio.Lock()

# pong 1:1 대기 class - 대기 큐에 등록후 매칭에 성공되면 웹소켓 url 응답
class PongQueueConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global pong_queue
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		async with pong_queue_lock:  # lock 걸고 큐 확인
			if self.intra_id in pong_queue: # 동일 intra id 로 웹소켓 연결 거절
				self.status = "denied" # 거절 상태 저장
				await self.close()
				return
			else:
				await self.accept()  # 웹소켓 연결 수락 후 대기 큐에 등록
				pong_queue.append(self.intra_id)
				self.status = "waiting"  # 상태 기다림으로 저장
				print("Pong 대기큐")
				print(pong_queue)

		self.user1_intra_id = "none"
		self.user2_intra_id = "none"
		self.running_task = asyncio.create_task(self.wait_for_match())

	async def disconnect(self, close_code):
		global pong_cross_check
		global pong_queue
		if self.status == "denied": # 동일 intra id 로 웹소켓 연결 거절 후 종료
			return
		self.running_task.cancel()
		if self.status == "waiting":  # 대기중 매치가 성사되지 않은 상태에서 퇴장(연결종료). 대기큐에서 제거
			async with pong_queue_lock:
				if self.intra_id in pong_queue:
					pong_queue.remove(self.intra_id)
		elif self.intra_id == self.user1_intra_id:  # user1 인지 확인 (대기열에서 삭제는 user1 에서만 진행)
			while True:
				async with pong_cross_lock:  # 매칭에 lock 걸고 서로의 아이디를 확인했는지 확인
					if pong_cross_check == 2:
						async with pong_queue_lock:  # 서로 확인했다면 lock 걸고 대기큐에서 삭제 (양쪽 모두)
							if self.user1_intra_id in pong_queue:
								pong_queue.remove(self.user1_intra_id)
							if self.user2_intra_id in pong_queue:
								pong_queue.remove(self.user2_intra_id)
						pong_cross_check = 0 # 다음 매칭을 위해 초기화
						break
					elif pong_cross_check == 0:
						break
				asyncio.sleep(1/20) # 1/20초 후 재확인

	async def wait_for_match(self):
		global pong_queue
		global pong_cross_check
		while True:  # 매칭 대기 루프
			async with pong_queue_lock:
				index = pong_queue.index(self.intra_id)
				length = len(pong_queue)
			if length > 1 and (index == 0 or index == 1): # 게임 매칭 조건: queue의 길이가 2 이상이면서, 나의 index가 0 or 1 이면 매칭가능
				async with pong_queue_lock:
					self.user1_intra_id = pong_queue[0]
					self.user2_intra_id = pong_queue[1]
				async with pong_cross_lock:  # lock 걸고 cross check +1 (상대방 아이디를 확인했다는 표시)
					pong_cross_check += 1
				await self.send(json.dumps({"match_url": f"/ws/pong/match/{self.user1_intra_id}_{self.user2_intra_id}/"})) # intra_id 조합하여 새 웹소켓 URL 생성 및 보내기
				self.status = "matched"
				await self.close()
			await asyncio.sleep(1/20)  # 1/20초 후 재확인


class PongMatchConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global pong_game_rooms
		self.match_name = self.scope['url_route']['kwargs']['match_name']  # URL에서 게임방 이름 가져오기
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']  # URL에서 intra id 가져오기

		await self.accept()  # 웹소켓 연결 수락

		if self.match_name not in pong_game_rooms: # 아직 생성되지 않았다면 게임매니저 객체 생성 및 게임 방에 등록
			pong_game_rooms[self.match_name] = PongGameManager()

		player1, player2 = self.match_name.split('_')  # 방 이름으로부터 역할 지정
		if self.intra_id == player1:
			self.role = "player1"
		elif self.intra_id == player2:
			self.role = "player2"

		async with asyncio.Lock():  # lock 걸고 내 상태를 off->on 으로 활성화
			pong_game_rooms[self.match_name].players_connection[self.role] = "on"
			pong_game_rooms[self.match_name].players_intra[self.role] = self.intra_id

		async with asyncio.Lock():  # 락걸고 두명 모두 on 이면 게임 시작
			if pong_game_rooms[self.match_name].players_connection["player1"] == "on" and pong_game_rooms[self.match_name].players_connection["player2"] == "on":
				pong_game_rooms[self.match_name].start_game_loop()

		self.timer = 0.0 # 타이머 초기화
		self.running_task = asyncio.create_task(self.send_position()) # 메인 함수인 send_position() 함수 시작


	async def disconnect(self, close_code):
		global pong_game_rooms
		self.running_task.cancel()
		async with asyncio.Lock():
			if self.match_name in pong_game_rooms and pong_game_rooms[self.match_name].players_connection[self.role] == "on":
				pong_game_rooms[self.match_name].players_connection[self.role] = "off"

		async with asyncio.Lock():
			if self.match_name in pong_game_rooms:
				if pong_game_rooms[self.match_name].players_connection["player1"] == "off" and pong_game_rooms[self.match_name].players_connection["player2"] == "off":
					del pong_game_rooms[self.match_name]

	async def receive(self, text_data): # player의 패들이동 입력받기 { "move": "up"/"down" }
		data = json.loads(text_data)
		if "move" in data:
			pong_game_rooms[self.match_name].move_paddle(self.role, data["move"])

	async def send_position(self): # 메인 함수 status(waiting > playing > saving > saved) 에 따라서 게임 진행
		global pong_game_rooms
		global time_limit
		while pong_game_rooms[self.match_name].status == "waiting" and self.timer < time_limit: # 시간 제한동안 매칭된 상대 입장을 기다림
			await asyncio.sleep(1/fps)
			self.timer += 1/fps
		if time_limit <= self.timer: # 만약 시간제한동안 매칭된 상대가 들어오지 않는다면 network_error 로 판단
			await pong_game_rooms[self.match_name].change_status("network_error")
			await self.send(text_data=json.dumps(
				pong_game_rooms[self.match_name].get_state()
			))
			await self.close()
			await asyncio.sleep(1)
		while pong_game_rooms[self.match_name].status == "playing": # 게임이 진행되는 동안 게임좌표를 player에게 보내기
			await self.send(text_data=json.dumps(
				pong_game_rooms[self.match_name].get_state()
			))
			await asyncio.sleep(1/fps)
		while pong_game_rooms[self.match_name].status != "saved": # 게임을 저장하는동안 기다림
			await asyncio.sleep(1)
		await self.send(text_data=json.dumps(  # 마지막 결과 보내주기
				pong_game_rooms[self.match_name].get_state()
		))
		await self.close()


class RPSQueueConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global rps_queue
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		async with rps_queue_lock:
			if self.intra_id in rps_queue: # 중복된 사용자 요청은 거절
				self.status = "denied" # 거절상태 저장
				self.close()
				return
			else:
				await self.accept()  # 웹소켓 연결 수락 및 대기큐 등록
				rps_queue.append(self.intra_id)
				self.status = "waiting" # 대기중 상태로 저장
				print("RPS 대기큐")
				print(rps_queue)

		self.user1_intra_id = "none"
		self.user2_intra_id = "none"
		self.running_task = asyncio.create_task(self.wait_for_match())

	async def disconnect(self, close_code):
		global rps_cross_check
		global rps_queue
		if self.status == "denied": # 거절된 요청은 바로 종료
			return
		self.running_task.cancel()  # 메인 함수 (비동기) 종료
		if self.status == "waiting":  # 매칭이 안된 상태에서 종료
			async with rps_queue_lock:
				if self.intra_id in rps_queue:
					rps_queue.remove(self.intra_id)  # 매칭이 안되고 대기열에서 삭제 후 종료
		elif self.intra_id == self.user1_intra_id:  # user1 인지 확인 (대기열에서 삭제는 한쪽에서만 진행)
			while True:
				async with rps_cross_check_lock:  # 매칭에 lock 걸고 서로의 아이디를 확인했는지 확인
					if rps_cross_check == 2:
						async with rps_queue_lock:  # 서로 확인했다면 lock 걸고 대기큐에서 삭제 (양쪽 모두)
							if self.user1_intra_id in rps_queue:
								rps_queue.remove(self.user1_intra_id)
							if self.user2_intra_id in rps_queue:
								rps_queue.remove(self.user2_intra_id)
						rps_cross_check = 0 # 다음 매칭을 위해 초기화
						break
				asyncio.sleep(1) # 1초후 재확인

	async def wait_for_match(self):
		global rps_queue
		global rps_cross_check  # 전역 변수 선언
		while True:   # 매칭 대기 루프: queue의 길이가 2 이상이면서, 나의 index가 0 or 1 이면 매칭가능
			async with rps_queue_lock:
				index = rps_queue.index(self.intra_id)
				length = len(rps_queue)
			if length > 1 and (index == 0 or index == 1):
				self.status = "matched"
				async with rps_queue_lock:     # lock 걸고 매칭된 intra_id 가져오기
					self.user1_intra_id = rps_queue[0]
					self.user2_intra_id = rps_queue[1]

				async with rps_cross_check_lock:  # lock 걸고 크로스 체크 +1
					rps_cross_check += 1
				await self.send(json.dumps({"match_url": f"/ws/rps/match/{self.user1_intra_id}_{self.user2_intra_id}/"})) # intra_id 조합하여 새 웹소켓 URL 생성 및 보내기
				await self.close()
			await asyncio.sleep(1)  # 1초 대기 후 재확인


class RPSMatchConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global rps_game_rooms
		self.match_name = self.scope['url_route']['kwargs']['match_name']  # URL에서 게임방 이름 가져오기
		self.intra_id = self.scope['url_route']['kwargs']['intra_id']

		await self.accept()  # 웹소켓 연결 수락

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
			length = len(rps_game_rooms[self.match_name].connection)
		if length == 2:
			await rps_game_rooms[self.match_name].change_status("playing")

		self.timer = 0.0
		self.running_task = asyncio.create_task(self.send_status())

	async def disconnect(self, close_code):
		global rps_game_rooms
		self.running_task.cancel() # 메인 함수 (비동기) 종료
		async with asyncio.Lock(): # if 선택을 안한 상황에서 종료시 자동으로 선택
			if self.role not in rps_game_rooms[self.match_name].choice:
				await rps_game_rooms[self.match_name].save_choice(self.role, await self.random_RPS())

		async with asyncio.Lock():  # 나갈때 나의 상태 off 변경
			if self.match_name in rps_game_rooms and rps_game_rooms[self.match_name].connection[self.role] == "on":
				rps_game_rooms[self.match_name].connection[self.role] = "off"

		async with asyncio.Lock():  # 두번째 off 하는 사람이 매니저 객체 삭제
			if len(rps_game_rooms[self.match_name].connection) == 2:
				if rps_game_rooms[self.match_name].connection["player1"] == "off" and rps_game_rooms[self.match_name].connection["player2"] == "off":
					del rps_game_rooms[self.match_name]
			elif len(rps_game_rooms[self.match_name].connection) == 1:
				del rps_game_rooms[self.match_name]


	async def receive(self, text_data): # player의 선택 전달받기
		global rps_game_rooms
		data = json.loads(text_data)
		if "choice" in data:
			await rps_game_rooms[self.match_name].save_choice(self.role, data["choice"])

	async def send_status(self): # 클라이언트에게 상황 전달
		global rps_game_rooms
		global time_limit
		while await rps_game_rooms[self.match_name].get_status() == "waiting" and self.timer < time_limit: # 제한 시간동안 상대방이 들어오기까지 대기
			await asyncio.sleep(1/fps)
			self.timer += 1/fps
		if time_limit <= self.timer: # 시간제한이 지나도록 상대가 들어오지 않으면 network_error로 간주
			await rps_game_rooms[self.match_name].change_status("network_error")
			await self.send(text_data=json.dumps( # 시작신호 주고 10(?!)초 기다리기 (프론트에서 카운트 다운)//
				{"status": "network_error"}
			))
			await self.close()
			await asyncio.sleep(1)
		else:
			await self.send(text_data=json.dumps( # 시작신호 주고 10(?!)초 기다리기 (프론트에서 카운트 다운)//
				{"status": "start"}
			))
			asyncio.sleep(10)

		while await rps_game_rooms[self.match_name].get_status() == "playing": # 두 플레이어 모두 선택이 전달될때까지 대기
			await asyncio.sleep(1)

		while await rps_game_rooms[self.match_name].get_status() == "saving": # 결과를 저장할동안 대기
			await asyncio.sleep(1)

		data = await rps_game_rooms[self.match_name].get_data() # 게임 내용 가져오기
		await self.send(text_data=json.dumps(  # 게임 결과 전달하기
			{
				"status": "finished",
				"result": data["result"][self.role],
				"opponent_choice": data["choice"][self.opponent],
			}
		))
		await self.close()

	async def random_RPS(self): # 선택을 하지 않았을 경우 랜덤으로 정해주기
		num = random.randint(0, 2)
		if num == 0:
			return "rock"
		elif num == 1:
			return "paper"
		elif num == 2:
			return "scissors"
