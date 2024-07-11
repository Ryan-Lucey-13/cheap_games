from django.urls import path

from apps.core import views

urlpatterns = [
    path('', views.game_info, name='home'),
    path('new-panel', views.create_panel, name='new_panel'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('pricing', views.game_discount, name='discount'),
    path('ratings', views.game_ratings, name='ratings'),
    path('panel-delete/<panel_id>/', views.delete_panel),
    path('panel-update/<panel_id>/', views.update_panel),
    path('favorite-game/create', views.favorite_game_create, name='favorite_game_create'),
]