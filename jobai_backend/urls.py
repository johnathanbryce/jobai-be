

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/users/', include('users.urls')), # will handle all url pathways for users api
    path('api/job_postings/', include('job_postings.urls')),  # will handle all url pathways for job_postings
    path('api/gmail/', include('gmail_integration.urls')) # will handle all url pathways for gmail_integration

]
