import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import JobPosting
from users.models import User
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
import logging
from django.utils import timezone

logger = logging.getLogger('job_postings')

@csrf_exempt
def get_job_postings(request):
    """
    API endpoint to retrieve job postings for a user.
    """
    if request.method == "GET":
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return JsonResponse({"error": "No Authorization header"}, status=400)

        token_type, _, access_token = auth_header.partition(" ")
        if token_type.lower() != "bearer":
            return JsonResponse({"error": "Invalid token type"}, status=400)

        user_email = request.GET.get("user_email")
        if not user_email:
            return JsonResponse({"error": "User email not provided"}, status=400)

        try:
            user = User.objects.get(email=user_email)
            # logger.info(f'User found: {user_email}')
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            logger.error(f'Error fetching user: {str(e)}')
            return JsonResponse({"error": "Error fetching user"}, status=500)

        # Retrieve job postings that are not deleted, ordered by most recent
        job_postings = JobPosting.objects.filter(user=user, is_deleted=False).order_by('-fetched_at')
        logger.info(f'Retrieved {job_postings.count()} job postings for user {user_email}')

        # Serialize job postings with all relevant fields
        serialized_jobs = []
        for job in job_postings:
            try:
                serialized_job = {
                    "job_uuid": str(job.job_uuid),
                    "title": job.title,
                    "company_name": job.company_name,
                    "location": job.location,
                    "salary": job.salary,
                    "job_type": job.job_type,
                    "date_posted": job.date_posted.isoformat() if job.date_posted else None,
                    "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                    "benefits": job.benefits,
                    "summary": job.summary,
                    "experience_level": job.experience_level,
                    "industries": job.industries,
                    "skills": job.skills,
                    "job_description_snippet": job.job_description_snippet,
                    "status": job.status,
                    "employment_type": job.employment_type,
                    "company_url": job.company_url,
                    "company_logo_url": job.company_logo_url,
                    "job_url": job.job_url if hasattr(job, 'job_url') else None,  # Safe access
                    "match_score": job.match_score,
                    "source": job.source,
                    "gmail_message_id": job.gmail_message_id,
                    "gmail_thread_id": job.gmail_thread_id,
                    "fetched_at": job.fetched_at.isoformat(),
                    "created_at": job.created_at.isoformat(),
                    "updated_at": job.updated_at.isoformat(),
                }
                serialized_jobs.append(serialized_job)
            except AttributeError as ae:
                logger.error(f"AttributeError while serializing job {job.id}: {str(ae)}")
            except Exception as e:
                logger.error(f"Unexpected error while serializing job {job.id}: {str(e)}")

        return JsonResponse({"job_postings": serialized_jobs}, status=200)
    else:
        logger.warning(f"Received invalid request method: {request.method}")
        return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def save_job_postings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_email = data.get("user_email")  
            job_postings = data.get("job_postings", [])

            if not user_email or not job_postings:
                logger.error("Invalid data: Missing user_email or job_postings")
                return JsonResponse({"error": "Invalid data"}, status=400)

            try:
                user = User.objects.get(email=user_email)
                logger.info(f'User found: {user_email}')
            except User.DoesNotExist:
                logger.error(f'User not found: {user_email}')
                return JsonResponse({"error": "User not found"}, status=404)
            except Exception as e:
                logger.error(f'Error fetching user: {str(e)}')
                return JsonResponse({"error": "Error fetching user"}, status=500)

            new_jobs = []
            for job in job_postings:
                gmail_id = job.get("gmail_message_id")
                job_url = job.get("job_url")
                if not gmail_id:
                    # logger.warning(f'Skipping job posting without gmail_message_id: {job}')
                    continue

                # Check for existing job posting with the same gmail_id and job_url
                if JobPosting.objects.filter(gmail_message_id=gmail_id, job_url=job_url, is_deleted=False).exists():
                    # logger.info(f"JobPosting with gmail_message_id {gmail_id} and job_url {job_url} already exists; skipping.")
                    continue

                fetched_at_str = job.get("fetched_at")
                fetched_at = parse_datetime(fetched_at_str)
                if not fetched_at:
                    logger.warning(f'Invalid fetched_at format: {fetched_at_str}')
                    continue

                date_posted_str = job.get("date_posted")
                date_posted = parse_datetime(date_posted_str) if date_posted_str else None

                application_deadline_str = job.get("application_deadline")
                application_deadline = parse_datetime(application_deadline_str) if application_deadline_str else None

                new_job = JobPosting(
                    user=user,
                    title=job.get("title", "No Title"),
                    company_name=job.get("company_name", "N/A"),
                    company_url=job.get("company_url"),
                    company_logo_url=job.get("company_logo_url"),
                    location=job.get("location", "N/A"),
                    employment_type=job.get("employment_type"),
                    job_type=job.get("job_type"),
                    date_posted=date_posted,
                    application_deadline=application_deadline,
                    salary=job.get("salary"),
                    benefits=job.get("benefits"),
                    summary=job.get("summary"),
                    experience_level=job.get("experience_level"),
                    industries=job.get("industries"),
                    skills=job.get("skills"),
                    job_description_snippet=job.get("job_description_snippet"),
                    status=job.get("status"),
                    match_score=job.get("match_score"),
                    fetched_at=fetched_at,
                    source=job.get("source", "Unknown"),
                    gmail_message_id=gmail_id,
                    gmail_thread_id=job.get("gmail_thread_id"),
                    job_url=job_url,
                )
                new_jobs.append(new_job)
                # logger.debug(f"Prepared new job posting: {new_job}")

            # Bulk create all new job postings
            JobPosting.objects.bulk_create(new_jobs)
            saved_count = len(new_jobs)
            logger.info(f"Total job postings saved: {saved_count}")

            return JsonResponse({"success": True, "saved_count": saved_count}, status=201)
        
        except json.JSONDecodeError:
            logger.error('Invalid JSON received')
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f'Error saving job postings: {str(e)}')
            return JsonResponse({"error": str(e)}, status=500)
    else:
        logger.error('Invalid request method for save_job_postings')
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def delete_job_posting(request, job_uuid):
    """
    API endpoint to soft delete a job posting from the database.
    """
    if request.method == "DELETE": 
        logger.info(f"DELETE request received for job_uuid: {job_uuid}")
        try:
            # Retrieve the JobPosting object by job_uuid
            job_posting = JobPosting.objects.get(job_uuid=job_uuid, is_deleted=False)
        except JobPosting.DoesNotExist:
            logger.warning(f"JobPosting with job_uuid {job_uuid} does not exist.")
            return JsonResponse({'success': False, 'error': 'Job posting not found.'}, status=404)
        except Exception as e:
            logger.error(f"Error retrieving JobPosting: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while retrieving the job posting.'}, status=500)
        
        try:
            # Soft delete the JobPosting
            job_posting.is_deleted = True
            job_posting.deleted_at = timezone.now()
            job_posting.save()
            logger.info(f"JobPosting with job_uuid {job_uuid} marked as deleted.")
            return JsonResponse({'success': True, 'job_uuid': job_uuid}, status=200)
        except Exception as e:
            logger.error(f"Failed to soft delete JobPosting: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while deleting the job posting.'}, status=500)
    else:
        logger.warning(f"Received non-DELETE request: {request.method}")
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)


        