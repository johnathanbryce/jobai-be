from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GmailCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refresh_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Gmail Credentials"