from rest_framework import serializers
from .models import User

# convert django mode instance data to JSON data
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__' # transform all fields 