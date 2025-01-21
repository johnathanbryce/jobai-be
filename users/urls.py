from django.urls import path
from . import views
from .views import get_users, create_user, create_user_via_oauth

urlpatterns = [
    path('', views.get_users, name='get_user'),  
    path('create/', views.create_user, name='create_user'),  
    path('oauth-sync/', create_user_via_oauth, name='create_user_via_oauth'),
]