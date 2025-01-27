from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.http import JsonResponse

import re
from bs4 import BeautifulSoup

def fetch_recent_emails(access_token, from_email, max_results=5):
    """
    Fetch recent emails from Gmail using the provided access token.
    Return emails based on the sender's email address and parse the content accordingly.
    """
    try:
        # Initialize the Gmail API client
        creds = Credentials(token=access_token)
        service = build('gmail', 'v1', credentials=creds)

        # Use the Gmail API query to fetch emails from the specified sender
        query = f"from:{from_email}"
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        # Fetch details for each message
        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')

            # Extract the email body
            body = None
            if 'data' in payload.get('body', {}):
                # If the body is directly available
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif 'parts' in payload:
                # If the body is split into parts (common for HTML emails)
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/html':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break

            # Parse the email body based on the sender
            jobs = []
            if body:
                soup = BeautifulSoup(body, 'html.parser')

                if from_email == "jobalerts-noreply@linkedin.com":
                    # Parse LinkedIn job alerts
                    main_job = soup.find('div', text=re.compile("Your job alert for"))
                    if main_job:
                        jobs.append(main_job.get_text(strip=True))

                    other_jobs_section = soup.find('h3', text=re.compile("Other jobs you might be interested in"))
                    if other_jobs_section:
                        other_jobs = other_jobs_section.find_next('ul')  # Assuming jobs are in a list
                        if other_jobs:
                            for job in other_jobs.find_all('li'):
                                jobs.append(job.get_text(strip=True))
                
                elif from_email == "alert@indeed.com":
                    # Parse Indeed job alerts
                    job_sections = soup.find_all('a', href=True, text=re.compile("View job"))
                    for job_section in job_sections:
                        jobs.append(job_section.get_text(strip=True))

            # Add parsed email details
            emails.append({
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'jobs': jobs,  # List of extracted job listings
            })

        return emails

    except Exception as e:
        return {"error": str(e)}


@csrf_exempt
def fetch_emails_view(request):
    """
    Django view to fetch recent emails.
    """
    if request.method == "POST":
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return JsonResponse({"error": "No Authorization header"}, status=400)

        # Extract Bearer token
        token_type, _, access_token = auth_header.partition(" ")
        if token_type.lower() != "bearer":
            return JsonResponse({"error": "Invalid token type"}, status=400)

        # Define the list of senders to fetch emails from
        senders = ["jobalerts-noreply@linkedin.com", "alert@indeed.com"]
        all_emails = []

        for sender in senders:
            # Fetch recent emails for each sender
            emails = fetch_recent_emails(access_token, sender, max_results=5)
            if isinstance(emails, dict) and "error" in emails:
                return JsonResponse({"error": emails["error"]}, status=500)
            all_emails.extend(emails)

        # Simplified implementation
        return JsonResponse(all_emails, safe=False, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)
