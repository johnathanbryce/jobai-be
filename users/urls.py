from django.urls import path
from . import views
from .views import get_users, create_user

urlpatterns = [
    path('', views.get_users, name='get_user'),  
    path('create/', views.create_user, name='create_user'),  
]