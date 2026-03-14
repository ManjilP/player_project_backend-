from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import Player

from players.serializers import (
   IndividualPlayerDetailSerializer,
   PlayerListSerializer,
)

class IndividualPlayerDetailAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)

   def get(self, request, slug=None, *args, **kwargs):
      if slug is None:
         try:
            player = Player.objects.select_related('user').get(user=request.user)
         except Player.DoesNotExist:
            return Response(
               {'message': "You are not a player!"},
               status=status.HTTP_404_NOT_FOUND
            )
      else:
         try:
            player = Player.objects.select_related('user').get(slug=slug)
         except Player.DoesNotExist:
            return Response(
               {'message': "Player doesn't exist!"},
               status=status.HTTP_404_NOT_FOUND
            )
         
      serializer = IndividualPlayerDetailSerializer(player)
      return Response(
         {
            'player': serializer.data
         },
         status=status.HTTP_200_OK
      )
   

class PlayersListAPIView(generics.ListAPIView):
   queryset = Player.objects.select_related('user').all()
   serializer_class = PlayerListSerializer
   permission_classes = (IsAuthenticated,)