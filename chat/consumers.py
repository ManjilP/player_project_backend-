from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from chat.mqtt_client import client

class ChatConsumer(AsyncWebsocketConsumer):
   async def connect(self):
      self.room_name = self.scope["url_route"]["kwargs"]['room_name']
      self.room_group_name = f"chat_{self.room_name}"

      print(f"Channel Name: {self.channel_name}")

      await self.channel_layer.group_add(self.room_group_name, self.channel_name)
      await self.accept()


   async def disconnect(self, close_code):
      await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


   async def receive(self, text_data):
      data = json.loads(text_data)
      message = data["message"]
      sender = data["sender"]


      payload = json.dumps({"room": self.room_name, "sender": sender, "message": message})

      await self.send_message_via_mqtt(payload)


   async def send_message_via_mqtt(self, payload):
      loop = asyncio.get_event_loop()
      await loop.run_in_executor(None, lambda: client.publish(f"chat/{self.room_name}", payload))


   async def chat_message(self, event):
      await self.send(text_data=json.dumps({
         "message": event["message"],
         "sender": event["sender"]
      }))