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
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            logger.error(f'Error fetching user: {str(e)}')
            return JsonResponse({"error": "Error fetching user"}, status=500)

        job_postings = JobPosting.objects.filter(user=user, is_deleted=False).order_by('-fetched_at')
        serialized_jobs = [
            {
                "title": job.title,
                "source": job.source,
                "gmail_message_id": job.gmail_message_id,
                "fetched_at": job.fetched_at.isoformat(),
            }
            for job in job_postings
        ]

        return JsonResponse({"job_postings": serialized_jobs}, status=200)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def save_job_postings(request):
    """
    API endpoint to save job postings to the database.
    Implements soft deletion handling.
    """
    if request.method == "POST":
        logger.info('save_job_postings POST request received')
        try:
            data = json.loads(request.body)
            user_email = data.get("user_email")  
            job_postings = data.get("job_postings", [])

            if not user_email or not job_postings:
                logger.error("Invalid data: Missing user_email or job_postings")
                return JsonResponse({"error": "Invalid data"}, status=400)

            # Attempt to fetch the user by email
            try:
                user = User.objects.get(email=user_email)
                logger.info(f'User found: {user_email}')
            except User.DoesNotExist:
                logger.error(f'User not found: {user_email}')
                return JsonResponse({"error": "User not found"}, status=404)
            except Exception as e:
                logger.error(f'Error fetching user: {str(e)}')
                return JsonResponse({"error": "Error fetching user"}, status=500)

            saved_count = 0 # tracks num of saved job postings
            for job in job_postings:
                gmail_id = job.get("gmail_message_id")
                if not gmail_id:
                    logger.warning(f'Skipping job posting without gmail_message_id: {job}')
                    continue

                try:
                    existing_job = JobPosting.objects.get(gmail_message_id=gmail_id)
                    # targets the is_deleted boolean flag col for each job_posting to ensure it is not displayed to the user
                    if existing_job.is_deleted:
                        logger.info(f"JobPosting {gmail_id} was deleted; skipping re-save.")
                        continue
                    else:
                        logger.info(f"JobPosting {gmail_id} already exists; skipping.")
                        continue
                except JobPosting.DoesNotExist:
                    # proceed to create new job posting
                    pass
                except Exception as e:
                    logger.error(f"Error checking existing JobPosting: {e}")
                    continue

                # Parse fetched_at into datetime object
                fetched_at_str = job.get("fetched_at")
                fetched_at = parse_datetime(fetched_at_str)
                if not fetched_at:
                    logger.warning(f'Invalid fetched_at format: {fetched_at_str}')
                    continue

                # Create the new JobPosting
                JobPosting.objects.create(
                    user=user,
                    title=job.get("title", "No Title"),
                    source=job.get("source", "Unknown"),
                    gmail_message_id=gmail_id,
                    fetched_at=fetched_at,
                )
                saved_count += 1
                logger.info(f"JobPosting {gmail_id} saved successfully.")

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
def delete_job_posting(request, emailId):
    """
    API endpoint to soft delete a job posting from the database.
    """
    if request.method == "DELETE": 
        logger.info(f"DELETE request received for emailId: {emailId}")
        try:
            # Retrieve the JobPosting object
            job_posting = JobPosting.objects.get(gmail_message_id=emailId)
        except JobPosting.DoesNotExist:
            logger.warning(f"JobPosting with gmail_message_id {emailId} does not exist.")
            return JsonResponse({'success': False, 'error': 'Job posting not found.'}, status=404)
        except Exception as e:
            logger.error(f"Error retrieving JobPosting: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while retrieving the job posting.'}, status=500)
        
        try:
            # Soft delete the JobPosting (marks the is_deleted and deleted_at columns in our database)
            # cron task eventually deletes this job_posting permanently from our db after X amount of days 
            job_posting.is_deleted = True
            job_posting.deleted_at = timezone.now()
            job_posting.save()
            logger.info(f"JobPosting with gmail_message_id {emailId} marked as deleted.")
            return JsonResponse({'success': True, 'email_id': emailId}, status=200)
        except Exception as e:
            logger.error(f"Failed to soft delete JobPosting: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while deleting the job posting.'}, status=500)
    else:
        logger.warning(f"Received non-DELETE request: {request.method}")
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)

        