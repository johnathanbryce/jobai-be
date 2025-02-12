# Generated by Django 5.1.4 on 2025-01-30 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job_postings", "0005_remove_jobposting_link_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobposting",
            name="job_url",
            field=models.URLField(
                blank=True, help_text="Direct URL to the job posting.", null=True
            ),
        ),
    ]
