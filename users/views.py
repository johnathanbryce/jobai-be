from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user_via_oauth(request):
    """
    1. Expect an ID token or access token from the request data.
    2. Verify that token with Google.
    3. Extract user info (email, name, google_id, profile_image_url).
    4. Create or update the User record in the database.
    5. Return the serialized user.
    """
    data = request.data
    print('user data', data)

     # Extract fields from the incoming request
    google_id = data.get("google_id")
    email = data.get("email")
    username = data.get("username") or (email.split("@")[0] if email else None)
    profile_image_url = data.get("profile_image_url")
    first_name = data.get("first_name") or username.split(" ")[0] # fallback is first word from username
    last_name = data.get("last_name") or username.split(" ")[1] # fallback is second word from username
    print('names', first_name, last_name)


    if not email or not google_id:
        return Response(
            {"error": "email and google_id are required fields."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Either get the existing user by email or create a new one.
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": username,
            "google_id": google_id,
            "profile_image_url": profile_image_url,
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    # If user already exists, update any details if needed.
    if not created:
        if google_id:
            user.google_id = google_id
        if profile_image_url:
            user.profile_image_url = profile_image_url
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

    # Serialize the user data for the response.
    serializer = UserSerializer(user)
    return Response(
        {
            "user": serializer.data,
            "is_new_user": created,
            "message": "User created successfully." if created else "User updated successfully."
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)  #deserialize  to convert to Django Model Instance
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

