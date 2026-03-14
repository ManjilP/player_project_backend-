import re

from rest_framework import serializers

from accounts.models import User, Player

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class LoginSerializer(serializers.Serializer):
   email = serializers.EmailField()
   password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

   def validate(self, attrs):
      email = attrs.get('email').lower()
      password = attrs.get('password')

      if not email and not password:
         raise serializers.ValidationError("Please provide both email and password.")
      
      if not User.objects.filter(email=email).exists():
         raise serializers.ValidationError("Email doesn't exist, register yourself first to login.")
      
      user = authenticate(request=self.context.get('request'), email=email, password=password)

      if not user:
         raise serializers.ValidationError("Wrong Credentials!")
      
      attrs['user'] = user
      return attrs
   

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError("Current Password is Incorrect!")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match!")
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        password = attrs['new_password']
        if not re.search("[_@$]", password):
            raise serializers.ValidationError(
                {"password": "Password must include at least one special character."}
            )

        return attrs
    

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': "password"})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': "password"})

    class Meta:
        model = User
        fields = ('name', 'email', 'contact', 'date_of_birth', 'photo', 'favorite_player', 'favorite_team', 'password', 'confirm_password', 'role')


    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match!")
        
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        password = attrs['password']
        if not re.search("[_@$]", password):
            raise serializers.ValidationError(
                {"password": "Password must include at least one special character."}
            )

        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)
    

class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'date_of_birth', 'photo', 'contact', 'favorite_team', 'favorite_player')


