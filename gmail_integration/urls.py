from django.urls import path
from .views import fetch_emails_view

urlpatterns = [
    path('fetch-emails/', fetch_emails_view, name='fetch_emails')
]