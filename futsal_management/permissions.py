from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
   def has_permission(self, request, view):
      return request.user.is_authenticated and request.user.role == "MANAGER"
   

class IsManagerOrReadOnly(BasePermission):
   def has_permission(self, request, view):
      if request.method in permissions.SAFE_METHODS:
         return True
      
      return request.user.is_authenticated and request.user.role == "MANAGER"
   

class IsPlayer(BasePermission):
   def has_permission(self, request, view):
      return request.user.is_authenticated and request.user.role == "PLAYER"