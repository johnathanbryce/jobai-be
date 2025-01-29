from django.urls import path
from . import views
from .views import save_job_postings, delete_job_posting

urlpatterns = [
    path('save-job-postings/', save_job_postings, name='save_job_postings'),  
    path('<str:emailId>/', delete_job_posting, name='delete_job_posting'),
    # TODO: path('api/job-postings/<str:emailId>/', save_job_posting, name='save_job_posting'),
]