from django.urls import path
from games import views
from games import api_views

urlpatterns = [
    path('', views.WelcomeView.as_view(), name='home'),
    path('games-list/', views.WaitingGamesListView.as_view(), name='games_list'),
    path('new-game/', views.NewGameView.as_view(), name='new_game'),
    path('client/<int:game_id>/', views.ClientView.as_view(), name='client'),
]
