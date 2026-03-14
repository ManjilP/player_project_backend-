from django.db import models
from accounts.models import User

# Create your models here.
class BaseChatModel(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)
   created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_creator')

   class Meta:
      abstract = True



class ChatRoom(BaseChatModel):
   name = models.CharField(max_length=255)
   members = models.ManyToManyField(User, related_name='room_members')
   is_group = models.BooleanField(default=True)

   def __str__(self):
      return self.name
   

class Message(models.Model):
   room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='room_messages')
   sender = models.ForeignKey(User, on_delete=models.CASCADE)
   content = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f"{self.sender.name}: {self.content[:20]}"