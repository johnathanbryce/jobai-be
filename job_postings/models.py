# job_postings/models.py
from django.db import models
from django.conf import settings
from users.models import User
# If your user_preferences is in a different app, import it here
# from user_preferences.models import UserPreferences

class JobPosting(models.Model):
    """
    Represents a single job posting (or email referencing a job).
    This is cached locally in the DB after fetching from Gmail or other sources.
    """

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_postings"
    )

    # Uncomment if I link to user_preferences:
    # preferences = models.ForeignKey(
    #     UserPreferences,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True
    # )

    # Core Job Info
    title = models.TextField()
    company_name = models.TextField(null=True, blank=True)
    company_url = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)  
    years_experience = models.CharField(max_length=50, null=True, blank=True)  
    skills = models.JSONField(null=True, blank=True)  # or TextField if you prefer storing as text
    salary = models.CharField(max_length=100, null=True, blank=True)  # or IntegerField
    link = models.URLField(null=True, blank=True)  
    source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="e.g. 'Indeed', 'LinkedIn', 'Gmail', etc."
    )

    # Email/Gmail-Specific Fields
    gmail_message_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Unique Gmail message ID if fetched from Gmail"
    )
    gmail_thread_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional Gmail thread ID"
    )
    fetched_at = models.DateTimeField(auto_now_add=True)

    # AI / Matching Fields
    summary = models.TextField(null=True, blank=True)
    match_score = models.FloatField(null=True, blank=True, help_text="Match score to user preferences")

    # Status / Management
    is_deleted = models.BooleanField(default=False, help_text="If user removes or hides posting")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title[:50]} - {self.company_name or 'Unknown'}"

