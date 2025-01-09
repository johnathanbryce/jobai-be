from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)                                      # Unique email for login
    name = models.CharField(max_length=255, blank=True, null=True)              # Full name
    google_id = models.CharField(max_length=255, blank=True, null=True)         # from gmail OAuth
    profile_image_url = models.URLField(blank=True, null=True)                  # from gmail oAuth
    hashed_password = models.CharField(max_length=255, blank=True, null=True)   # For OPTIONAL password storage
    date_joined = models.DateTimeField(auto_now_add=True)                       # Auto-generated on user creation

    def __str__(self):
        return f"{self.name} ({self.email})"