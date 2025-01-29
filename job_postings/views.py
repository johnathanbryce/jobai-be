import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import JobPosting
from users.models import User
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
import logging


logger = logging.getLogger('job_postings')

@csrf_exempt
def save_job_postings(request):
    """
    API endpoint to save job postings to the database.
    """
    if request.method == "POST":
        logger.info('save_job_postings POST request received')
        try:
            data = json.loads(request.body)
            user_email = data.get("user_email")  
            job_postings = data.get("job_postings", [])

            #logger.debug(f'Received data: {data}')
            #logger.debug(f'Number of job postings: {len(job_postings)}')

            if not user_email or not job_postings:
                return JsonResponse({"error": "Invalid data"}, status=400)

            # Attempt to fetch the user by email
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)
            except Exception as e:
                logger.error(f'Error fetching user: {str(e)}')
                return JsonResponse({"error": "Error fetching user"}, status=500)

            saved_count = 0
            for job in job_postings:
                # Check for duplicate by Gmail message ID
                gmail_id = job.get("gmail_message_id")
                if not gmail_id:
                    logger.warning(f'Skipping job posting without gmail_message_id: {job}')
                    continue

                if not JobPosting.objects.filter(gmail_message_id=gmail_id).exists():
                    # Parse fetched_at into datetime object
                    fetched_at_str = job.get("fetched_at")
                    fetched_at = parse_datetime(fetched_at_str)
                    if not fetched_at:
                        logger.warning(f'Invalid fetched_at format: {fetched_at_str}')
                        continue

                    JobPosting.objects.create(
                        user=user,
                        title=job.get("title", "No Title"),
                        source=job.get("source", "Unknown"),
                        gmail_message_id=gmail_id,
                        fetched_at=fetched_at,
                    )
                    saved_count += 1
                else:
                    logger.info(f'Duplicate job posting found: {gmail_id}')

            return JsonResponse({"success": True, "saved_count": saved_count}, status=201)

        except json.JSONDecodeError:
            logger.error('Invalid JSON received')
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f'Error saving job postings: {str(e)}')
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import JobPosting
import logging

logger = logging.getLogger('job_postings')

@csrf_exempt
def delete_job_posting(request, emailId):
    """
    API endpoint to delete a job posting from the database.
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
            # Delete the JobPosting object
            job_posting.delete()
            logger.info(f"JobPosting with gmail_message_id {emailId} deleted successfully.")
            return JsonResponse({'success': True, 'email_id': emailId}, status=200)
        except Exception as e:
            logger.error(f"Failed to delete JobPosting: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while deleting the job posting.'}, status=500)
    else:
        logger.warning(f"Received non-DELETE request: {request.method}")
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)


        