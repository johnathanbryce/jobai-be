from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)                        # Unique email for login
    name = models.CharField(max_length=255)                       # Full name
    hashed_password = models.CharField(max_length=255, blank=True, null=True)  # For OPTIONAL password storage
    date_joined = models.DateTimeField(auto_now_add=True)         # Auto-generated on user creation

    def __str__(self):
        return f"{self.name} ({self.email})"


print(User)
