
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('lidar/<cmd>/', views.lidar),
    path('Main_cam/<cmd>/', views.Main_cam),
    path('keyboard/<cmd>/', views.keyboard),
]
