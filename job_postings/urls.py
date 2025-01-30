from django.urls import path
from . import views
from .views import get_job_postings, save_job_postings, delete_job_posting

urlpatterns = [
    path('', views.get_job_postings, name='get_job_postings'),
    path('save-job-postings/', save_job_postings, name='save_job_postings'),  
    path('<str:emailId>/', delete_job_posting, name='delete_job_posting'),
    # TODO: path('api/job-postings/<str:emailId>/', save_job_posting, name='save_job_posting'),
]