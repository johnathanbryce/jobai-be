# Generated by Django 5.1.4 on 2025-01-17 00:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_google_id_user_profile_image_url_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPreferences",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("skills", models.JSONField(blank=True, null=True)),
                ("locations", models.JSONField(blank=True, null=True)),
                (
                    "years_experience",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("salary", models.CharField(blank=True, max_length=50, null=True)),
                ("job_titles", models.JSONField(blank=True, null=True)),
                ("resume_file_path", models.TextField(blank=True, null=True)),
                ("additional_preferences", models.JSONField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preferences",
                        to="users.user",
                    ),
                ),
            ],
        ),
    ]
