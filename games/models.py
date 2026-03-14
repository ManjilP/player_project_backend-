import datetime
from datetime import timedelta

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import Player


class Futsal(models.Model):
   name = models.CharField(max_length=450)
   location = models.CharField(max_length=600)

   def __str__(self):
      return self.name


def get_next_friday():
   today = datetime.date.today()
   days_until_friday = (4 - today.weekday()) % 7
   if days_until_friday == 0:
      days_until_friday = 0
   next_friday = today + timedelta(days=days_until_friday)
   return next_friday



class Game(models.Model):
   game_id = models.CharField(max_length=15, unique=True, primary_key=True)
   date = models.DateField(default=get_next_friday)
   time = models.TimeField(default=datetime.time(18, 0, 0))
   available_players = models.ManyToManyField(
      Player,
      null=True,
      blank=True,
      related_name='game_players'
   )

   futsal = models.ForeignKey(Futsal, on_delete=models.CASCADE, related_name='venue')

   teamnameA = models.CharField(max_length=255, null=True, blank=True)
   logoA = models.ImageField(upload_to='team/logo/', null=True, blank=True)
   teamA = models.ManyToManyField(
      Player,
      null=True,
      blank=True,
      related_name='teamA'
   )

   teamnameB = models.CharField(max_length=255, null=True, blank=True)
   logoB = models.ImageField(upload_to='team/logo/', null=True, blank=True)
   teamB = models.ManyToManyField(
      Player,
      null=True,
      blank=True,
      related_name='teamB'
   )

   goalsA = models.IntegerField(default=0, validators=[MinValueValidator(0)])
   goalsB = models.IntegerField(default=0, validators=[MinValueValidator(0)])
   is_complete = models.BooleanField(default=False)

   class Meta:
      unique_together = ('date', 'time', 'futsal')

   def __str__(self):
      return self.game_id
   

   def create(self, validated_data):
      return Game.objects.create(**validated_data)


   def save(self, *args, **kwargs):
      if not self.game_id:
         try:
            last_game = Game.objects.order_by('-game_id').first()

            if last_game:
               last_id = int(last_game.game_id.split("_")[1])
               count = last_id+1
            else:
               count = 1
         
            self.game_id = f"GAME_{count:05d}"
         except Game.DoesNotExist:
            self.game_id = f"GAME_00001"

      super().save(*args, **kwargs)



class Goal(models.Model):
   game = models.ForeignKey(Game, on_delete=models.RESTRICT, related_name='goals')
   player = models.ForeignKey(Player, on_delete=models.RESTRICT, related_name='player_goals')
   assist = models.ForeignKey(Player, null=True, on_delete=models.RESTRICT, related_name='player_assists')

   def __str__(self):
      return f"Goal for {self.player} in {self.game}"
   

class PlayerGameRating(models.Model):
   game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_rating')
   player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_game_rating')
   rating = models.FloatField(default=5)

   def __str__(self):
      return f"Rating of {self.player} for {self.game}"


   def calculate_player_game_rating(self, player, game):
      player_goals = Goal.objects.filter(game=game, player=player).count()
      player_assists = Goal.objects.filter(game=game, assist=player).count()

      if player in game.teamA.all():
         team_goals = game.goalsA
         opponent_goals = game.goalsB
      else:
         team_goals = game.goalsB
         opponent_goals = game.goalsA

      if team_goals > opponent_goals:
         result_points = 1
      elif team_goals < opponent_goals:
         result_points = -1
      else:
         result_points = 0
      
      new_rating = 5 + (0.8 * player_goals) + (0.3 * player_assists) - (0.1 * opponent_goals) + result_points
      rating =  max(0, min(10, new_rating))

      if rating < 5:
         return 5 
      else:
         return rating
   

   def save(self, *args, **kwargs):
      self.rating = self.calculate_player_game_rating(self.player, self.game)
      super().save(*args, **kwargs)



class PlayerReviewRating(models.Model):
   rating_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='rating_player')
   game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_player')
   player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_game_review_rating')
   rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

   def __str__(self):
      return f"{self.game}_{self.player}"