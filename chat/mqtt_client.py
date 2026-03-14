import json
import paho.mqtt.client as mqtt

from django.conf import settings
from accounts.models import User
from chat.models import ChatRoom, Message

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


BROKER = settings.MQTT_BROKER
PORT = settings.MQTT_PORT


def on_connect(client, userdata, flags, rc):
   print("Connected with result code"+str(rc))
   client.subscribe("chat/#")


def on_message(client, userdata, msg):
   try:
      payload = json.loads(msg.payload.decode('utf-8'))
      sender = User.objects.get(email=payload["sender"])
      room = ChatRoom.objects.get(name=payload['room'])
      
      Message.objects.create(room=room, sender=sender, content=payload['message'])

      channel_layer = get_channel_layer()
      async_to_sync(channel_layer.group_send)(
         f"chat_{room.id}",
         {
            "type": "chat.message",
            "message": payload['message'],
            "sender":   sender.email
         }
      )

      print(f"Message received in {room.name}: {payload['message']}")
   except Exception as e:
      print(f"Error processing message: {e}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)


def start_mqtt():
   client.loop_start()