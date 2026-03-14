from rest_framework import serializers

from games.models import Game, Futsal

from players.serializers import PlayerListSerializer


class FutsalSerializer(serializers.ModelSerializer):
   class Meta:
      model = Futsal
      fields = ('id', 'name', 'location')


class GameListSerializer(serializers.ModelSerializer):
   futsal = FutsalSerializer(read_only=True)
   class Meta:
      model = Game
      fields = ('date', 'time', 'futsal', 'teamnameA', 'teamnameB', 'logoA', 'logoB', 'goalsA', 'goalsB', 'game_id')


class GameDetailSerializer(serializers.ModelSerializer):
   futsal = FutsalSerializer(read_only=True)
   teamA = PlayerListSerializer(many=True, read_only=True)
   teamB = PlayerListSerializer(many=True, read_only=True)

   class Meta:
      model = Game
      fields = ('date', 'time', 'futsal', 'teamA', 'teamB', 'teamnameA', 'teamnameB', 'logoA', 'logoB', 'goalsA', 'goalsB', 'is_complete')


class GameTeamUpdateSerializer(serializers.ModelSerializer):
   teamA = PlayerListSerializer(many=True, read_only=True)
   teamB = PlayerListSerializer(many=True, read_only=True)

   class Meta:
      model = Game
      fields = ('teamA', 'teamB')

   def to_representation(self, instance):
      request = self.context.get('request')
      if request and request.method == 'GET':
         return {
               'teamA': PlayerListSerializer(instance.teamA.all(), many=True).data,
               'teamB': PlayerListSerializer(instance.teamB.all(), many=True).data
         }
      return super().to_representation(instance)


class GameCreateSerializer(serializers.ModelSerializer):
   class Meta:
      model = Game
      fields = ('futsal', 'date', 'time')


class AvailablePlayersSerializer(serializers.ModelSerializer):
   available_players = PlayerListSerializer(many=True, read_only=True)
   
   class Meta:
      model = Game
      fields = ('available_players',)