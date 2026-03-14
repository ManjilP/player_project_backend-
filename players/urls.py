from django.urls import path

from players import views

app_name = "players"

urlpatterns = [
   path('', views.PlayersListAPIView.as_view(), name='player_list'),
   path('info/', views.IndividualPlayerDetailAPIView.as_view(), name='player_detail_view'),
   path('info/<slug:slug>/', views.IndividualPlayerDetailAPIView.as_view(), name='player_detail_view'),
]