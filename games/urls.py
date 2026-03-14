from django.urls import path

from games import views
from games.views import FutsalAPIView

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'futsals', FutsalAPIView, basename='futsal')

app_name = 'games'

urlpatterns = [
   path('get/', views.GameListAPIView.as_view(), name='games'),
   path('create/', views.GameCreateAPIView.as_view(), name='game_create'), 
   path('get/<str:game_id>/', views.GameDetailAPIView.as_view(), name='games'),

   path('get/<str:game_id>/register/', views.RegisterToGameAPIView.as_view(), name='register_to_game'),
   path('get/<str:game_id>/team/', views.TeamPlayersAPIView.as_view(), name='team_players'),
   path('get/<str:game_id>/players/', views.AvailablePlayersAPIView.as_view(), name='available_players'),
   path('get/<str:game_id>/goal/<str:player_id>/', views.AddGoalAPIView.as_view(), name='goal'),

   path('get/<str:game_id>/player/<str:player_id>/review/', views.PlayerReviewAPIView.as_view(), name='game_rating')
] 

urlpatterns += router.urls