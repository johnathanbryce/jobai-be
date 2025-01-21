from django.shortcuts import render
# gmail_integration/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Just for local testing. Add proper CSRF/token auth for production.
def fetch_emails_view(request):
    """
    1. Receive the Gmail access token from the client (in headers).
    2. Use the token to call the Gmail API for reading emails.
    3. Parse/filter the emails for job-related data.
    4. Return the relevant data as a JSON response.
    """
    if request.method == "POST":
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return JsonResponse({"error": "No Authorization header"}, status=400)

        # Typically looks like 'Bearer <access_token>'
        token_type, _, access_token = auth_header.partition(" ")
        if token_type.lower() != "bearer":
            return JsonResponse({"error": "Invalid token type"}, status=400)
        # print("DEBUG: ACCESS TOKEN -->", access_token) 

        body = json.loads(request.body)
        user_email = body.get("email")

        # TODO: use python library to handle parsing of emails (ex: google-api-python-client)
        # dummy response:
        return JsonResponse({
            "message": "Success!",
            "user_email": user_email,
            "access_token_snippet": access_token[:10] + "..."
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
