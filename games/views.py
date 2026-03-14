from django.http import Http404
from games.serializers import (
   GameDetailSerializer,
   FutsalSerializer,
   GameCreateSerializer,
   GameTeamUpdateSerializer,
   AvailablePlayersSerializer,
   GameListSerializer,
)

from games.models import Game, Futsal, PlayerReviewRating, Goal, PlayerGameRating

from accounts.models import Player

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from futsal_management.permissions import IsManager, IsManagerOrReadOnly, IsPlayer


class GameCreateAPIView(generics.GenericAPIView):
   queryset = Game.objects.all()
   serializer_class = GameCreateSerializer
   permission_classes = (IsManager,)

   def post(self, request, *args, **kwargs):
      data = request.data
      serializer = self.serializer_class(data=data)

      if serializer.is_valid():
         game = serializer.save()
         return Response(
            {
               'message': "Game Created Successfully!",
               'game': game.game_id # type: ignore
            },
            status=status.HTTP_201_CREATED
         )
      else:
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameListAPIView(generics.GenericAPIView):
   serializer_class = GameListSerializer

   def get(self, request, *args, **kwargs):
      match_type = request.query_params.get('type')

      if match_type == "upcoming":
         games = Game.objects.filter(is_complete=False)
      elif match_type == "completed":
         games = Game.objects.filter(is_complete=True)
      else:
         return Response(
            {'error': "The query parameter is not valid!"},
            status=status.HTTP_400_BAD_REQUEST
         )
      
      serializer = self.serializer_class(games, many=True)

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )



class GameDetailAPIView(generics.GenericAPIView):
   queryset = Game.objects.all()
   serializer_class = GameDetailSerializer
   permission_classes = (IsManagerOrReadOnly,)

   def get_game(self, game_id):
      try:
         return Game.objects.get(game_id=game_id), None
      except Game.DoesNotExist:
         return None, "No Game found with the provided Game ID."


   def get(self, request, game_id, *args, **kwargs):
      game, error_message = self.get_game(game_id)
      
      if not game:
         return Response(
            {'message': error_message},
            status=status.HTTP_404_NOT_FOUND
         )

      serializer = self.serializer_class(game)

      return Response(serializer.data, status=status.HTTP_200_OK)
   

   def patch(self, request, game_id, *args, **kwargs):
      game, error_message = self.get_game(game_id)

      if not game:
         return Response(
            {'message': error_message},
            status=status.HTTP_404_NOT_FOUND
         )
      
      if request.user.role != "MANAGER":
         return Response(
            {'message': "You are not authenticated to update the game info."},
            status=status.HTTP_401_UNAUTHORIZED
         )

      serializer = self.serializer_class(game, data=request.data, partial=True)
      if serializer.is_valid():
         serializer.save()
         return Response(
            {
               'message': "Game Updated successfully!",
               'data': serializer.data
            },
            status=status.HTTP_200_OK
         )
      else:
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
   def delete(self, request, game_id, *args, **kwargs):
      game, error_message = self.get_game(game_id)

      if not game:
         return Response(
            {'message': error_message},
            status=status.HTTP_404_NOT_FOUND
         )
      
      if request.user.role != "MANAGER":
         return Response(
            {'message': "You are not authenticated to delete the game info."},
            status=status.HTTP_401_UNAUTHORIZED
         )

      if game.is_complete:
         return Response(
            {'message': "Completed Game cannot be deleted!"},
            status=status.HTTP_400_BAD_REQUEST
         )

      game.delete()
      return Response(
         {'message': "Game deleted successfully!"}
      )


class FutsalAPIView(ModelViewSet):
   queryset = Futsal.objects.all()
   permission_classes = (IsAuthenticated,)
   serializer_class = FutsalSerializer



class RegisterToGameAPIView(APIView):
   permission_classes = (IsPlayer,)

   def post(self, request, game_id, *args, **kwargs):
      try:
         game = Game.objects.get(game_id=game_id)
      except Game.DoesNotExist:
         return Response(
            {'message': "Game doesn't exist!"},
            status=status.HTTP_404_NOT_FOUND
         )

      if game.is_complete == False: 
         user = request.user
         if user.role != "PLAYER":
            return Response(
               {'message': "You should be a player to register for the Game!"},
               status=status.HTTP_401_UNAUTHORIZED
            )
         
         if game.available_players.filter(id=user.player.id).exists():
            return Response(
               {'message': "You are already registered to the Game!"},
               status=status.HTTP_400_BAD_REQUEST
            )
         
         game.available_players.add(user.player)
         game.save()

         player_game_rating = PlayerGameRating.objects.create(
            game = game,
            player = user.player
         )
         player_game_rating.save()

         return Response(
            {'message': f"You have been registered for the game {game.game_id}"},
            status=status.HTTP_201_CREATED
         )
      else:
         return Response(
            {'message': "This game is already completed!"},
            status=status.HTTP_400_BAD_REQUEST
         )



class TeamPlayersAPIView(generics.GenericAPIView):
   queryset = Game.objects.all()
   serializer_class = GameTeamUpdateSerializer  

   def get(self, request, *args, **kwargs):
      game_id = kwargs.get('game_id')
      game = get_object_or_404(Game, game_id=game_id)

      serializer = self.serializer_class(game)

      return Response(
         serializer.data, status=status.HTTP_200_OK
      )


   def patch(self, request, *args, **kwargs):
      game_id = kwargs.get('game_id')
      game = get_object_or_404(Game, game_id=game_id)

      teamA_players = request.data.get('teamA', [])
      teamB_players = request.data.get('teamB', [])

      if teamA_players:
         for player_id in teamA_players:
               player = get_object_or_404(Player, id=player_id)
               if player in game.available_players.all():
                  game.teamA.add(player)

      if teamB_players:
         for player_id in teamB_players:
               player = get_object_or_404(Player, id=player_id)
               if player in game.available_players.all():
                  game.teamB.add(player)

      return Response(
         {
            'message': "Players successfully added!",
         },
         status=status.HTTP_200_OK
      )



class AvailablePlayersAPIView(generics.GenericAPIView):
   permission_classes = (IsManager,)
   serializer_class = AvailablePlayersSerializer

   def get(self, request, *args, **kwargs):
      game_id = kwargs.get('game_id')

      try:
         game = Game.objects.get(game_id=game_id)
      except Game.DoesNotExist:
         return Response(
            {'message': "There is no game for the given ID!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      serializer = self.serializer_class(game)

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )
   


class AddGoalAPIView(APIView):
   permission_classes = (IsManager,)

   def post(self, request, *args, **kwargs):
      game_id = kwargs.get('game_id')
      player_id = kwargs.get('player_id')
      assist = request.query_params.get('assist')

      if player_id == assist:
         assist = None

      try:
         game = Game.objects.get(game_id=game_id)
      except Game.DoesNotExist:
         return Response(
            {'error': "No Game Found!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      try:
         player = Player.objects.get(slug=player_id)
      except Player.DoesNotExist:
         return Response(
            {"error": "No such player found in this game!"},
            status=status.HTTP_404_NOT_FOUND
         )

      if player not in game.available_players.all():
         return Response(
            {'message': "Player is not in the Game!"},
            status=status.HTTP_400_BAD_REQUEST
         )

      if game.is_complete == False:
         self.update_game_goals(game, player)

         player.goals += 1
         player.save()

         assisting_player = None
         if assist:
            try:
               assisting_player = self.get_object_or_404(Player, slug=assist) # type: ignore
            except Http404:
               return Response(
                  {'message': "Assisting Player doesn't exist!"},
                  status=status.HTTP_404_NOT_FOUND
               )

         goal = Goal.objects.create(game=game, player=player, assist=assisting_player)

         goal_player_rating = PlayerGameRating.objects.get(player=player, game=game)
         goal_player_rating.save()

         if assisting_player:
            assist_player_rating = PlayerGameRating.objects.get(player=assisting_player, game=game)
            assist_player_rating.save()

            self.update_assists(assisting_player)

         return Response(
            {'message': "Goal recorded"},
            status=status.HTTP_201_CREATED
         )
      else:
         return Response(
            {'message': "This game is already completed!"},
            status=status.HTTP_400_BAD_REQUEST
         )
   

   def update_game_goals(self, game, player):
      if player in game.teamA.all():
         game.goalsA += 1
      elif player in game.teamB.all():
         game.goalsB += 1
      
      game.save()



   def update_assists(self, assist):
      try:
         assisting_player = Player.objects.get(slug = assist)
         assisting_player.assists += 1
         assisting_player.save() 
      except Player.DoesNotExist:
         pass
      


class PlayerReviewAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)

   def post(self, request, *args, **kwargs):
      game_id = kwargs.get('game_id')
      player_id = kwargs.get('player_id')
      rating = request.data.get('rating')

      if rating is None:
         return Response(
            {'error': "Rating is required!"},
            status=status.HTTP_400_BAD_REQUEST
         )

      game = get_object_or_404(Game, game_id=game_id)
      player = get_object_or_404(Player, slug=player_id)

      if game.is_complete == True:
         user = request.user
         
         if user in game.available_players:
            player_rating, created = PlayerReviewRating.objects.get_or_create(
               rating_player = user.player,
               game = game,
               player = player,
               rating = rating
            )
            player_rating.save()
         else:
            return Response(
               {'error': "You are not a player in this game!"},
               status=status.HTTP_400_BAD_REQUEST
            )
         
         if created:
            return Response(
               {'message': "Rating placed successfully!"},
               status=status.HTTP_201_CREATED
            )
         else:
            return Response(
               {'message': "You have already rated the player for this game."},
               status=status.HTTP_400_BAD_REQUEST
            )
      else:
         return Response(
            {'message': "You cannot rate the player before the game ends!"},
            status=status.HTTP_400_BAD_REQUEST
         )