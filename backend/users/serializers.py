from djoser.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from djoser.serializers import UserSerializer


class SpecialUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        ]
        read_only_fields = (settings.LOGIN_FIELD,)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']