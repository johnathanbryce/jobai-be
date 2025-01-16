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
    return 

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)  #deserialize  to convert to Django Model Instance
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

