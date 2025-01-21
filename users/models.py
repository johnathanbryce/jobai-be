from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Inherits all fields from AbstractUser (username, email, first_name, last_name etc.).
    Add your custom fields below.
    """
    google_id = models.CharField(max_length=255, blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.email})"



class UserPreferences(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="preferences"
    )
    skills = models.JSONField(null=True, blank=True)
    locations = models.JSONField(null=True, blank=True)
    years_experience = models.CharField(max_length=50, null=True, blank=True)
    salary = models.CharField(max_length=50, null=True, blank=True)
    job_titles = models.JSONField(null=True, blank=True)
    resume_file_path = models.TextField(null=True, blank=True)
    additional_preferences = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"