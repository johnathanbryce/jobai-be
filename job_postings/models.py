# job_postings/models.py

from django.db import models
from users.models import User

class JobPosting(models.Model):
    """
    Represents a single job posting (or email referencing a job).
    """

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_postings"  # Allows reverse querying: user.job_postings.all()
    )

    # Core Job Information
    title = models.TextField(help_text="Title of the job posting.")
    company_name = models.TextField(null=True, blank=True, help_text="Name of the company offering the job.")
    company_url = models.URLField(null=True, blank=True, help_text="URL to the company's website.")
    company_logo_url = models.URLField(null=True, blank=True, help_text="URL to the company's logo image.")
    location = models.TextField(null=True, blank=True, help_text="Location of the job.")
    job_url = models.URLField(
        null=True,
        blank=True,
        help_text="Direct URL to the job posting."
    )
    employment_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Nature of employment (e.g., Full-time, Part-time, Contract, Internship)."
    )
    job_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Specific type of job (e.g., Remote, On-site, Hybrid)."
    )
    date_posted = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the job was posted."
    )
    application_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Deadline to apply for the job."
    )

    # Compensation and Benefits
    salary = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Compensation details (e.g., $80,000 - $100,000)."
    )
    benefits = models.TextField(
        null=True,
        blank=True,
        help_text="Overview of benefits offered by the company."
    )

    # Job Description and Requirements
    summary = models.TextField(
        null=True,
        blank=True,
        help_text="Brief overview or key responsibilities of the job."
    )
    experience_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Required experience level (e.g., Junior, Mid-level, Senior)."
    )
    industries = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Relevant industries or sectors for the job."
    )
    skills = models.JSONField(
        null=True,
        blank=True,
        help_text="List of required or preferred skills."
    )
    job_description_snippet = models.TextField(
        null=True,
        blank=True,
        help_text="A brief snippet from the job description."
    )

    # Status and Management
    status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Current status of the job posting (e.g., Actively Recruiting)."
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the job posting has been soft-deleted."
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the job posting was soft-deleted."
    )
    fetched_at = models.DateTimeField(
        help_text="Timestamp when the job posting was fetched from the source."
    )

    # Email/Gmail-Specific Fields
    gmail_message_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique Gmail message ID if fetched from Gmail."
    )
    gmail_thread_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional Gmail thread ID."
    )

    # AI / Matching Fields
    match_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Match score to user preferences."
    )

    # Metadata
    source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Source of the job posting (e.g., 'Indeed', 'LinkedIn', 'Gmail')."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the job posting was created in the database."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the job posting was last updated in the database."
    )

    def __str__(self):
        return f"{self.title[:50]} - {self.source or 'Unknown'}"
