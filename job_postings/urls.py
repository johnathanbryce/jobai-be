from django.urls import path
from . import views
from .views import save_job_postings

urlpatterns = [
    path('save-job-postings', save_job_postings, name='save_job_postings'),  
]