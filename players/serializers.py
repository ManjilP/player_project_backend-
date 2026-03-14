from rest_framework import serializers

from accounts.models import Player


class PlayerListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    photo = serializers.ImageField(source='user.photo', read_only=True)
    age = serializers.CharField(source='user.age', read_only=True)

    class Meta:
        model = Player
        fields = ('name', 'rating', 'photo', 'age', 'slug')
        

class IndividualPlayerDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    photo = serializers.ImageField(source='user.photo', read_only=True)
    age = serializers.CharField(source='user.age', read_only=True)
    date_of_birth = serializers.CharField(source='user.date_of_birth', read_only=True)
    description = serializers.CharField(source='user.description', read_only=True)

    class Meta:
        model = Player
        fields = ('name', 'email', 'photo', 'age', 'date_of_birth', 'description', 'rating', 'goals', 'assists', 'games_played')


class PlayerCardSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    photo = serializers.ImageField(source='user.photo', read_only=True)

    class Meta:
        model = Player
        fields = ('name', 'photo', 'rating', 'games_played')