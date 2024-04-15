from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
        )
