import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_manager import GameManager

game_manager = {}

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		# self.user = self.scope['user']
		self.session_id = self.scope['url_route']['kwargs']['session_id']
		self.group_name = f"game_{self.session_id}"

		if self.session_id not in game_manager:
			game_manager[self.session_id] = GameManager()

		self.count = len(game_manager[self.session_id].players)
		self.player_id = f"player{self.count + 1}"
		game_manager[self.session_id].players[self.player_id] = self.player_id
		print(f"count: {self.count}")

		if self.count == 1:
			game_manager[self.session_id].status = "playing"
			game_manager[self.session_id].start_game_loop()

		await self.accept()

		self.running_task = asyncio.create_task(self.send_position())


	async def disconnect(self, close_code):
		if self.session_id in game_manager and self.player_id in game_manager[self.session_id].players:
			del game_manager[self.session_id].players[self.player_id]

		if not game_manager[self.session_id].players:
			del game_manager[self.session_id]

		await self.close()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if "move" in data:
			game_manager[self.session_id].move_paddle(data["role"], data["move"])

	async def send_position(self):
		while game_manager[self.session_id].status == "ready":
			print("waiting for player...")
			await asyncio.sleep(1/40)
		while game_manager[self.session_id].status == "playing":
			await asyncio.sleep(1/40)
			print("playing")
			print(game_manager[self.session_id].status)
			await self.send(text_data=json.dumps(
				game_manager[self.session_id].get_state()
			))
		while game_manager[self.session_id].status != "finished":
			print("saving the result...")
			await asyncio.sleep(1)
		await self.disconnect(1000)


