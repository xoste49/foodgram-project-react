from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from djoser.conf import settings

from .models import (
    Recipe,
    Tag, Ingredient, Subscription, Favorite
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    #is_subscribed = False

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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(many=False)
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField('get_image_url')

    @staticmethod
    def get_image_url(obj):
        return obj.image.url

    class Meta:
        fields = (
            'id', 'tags', 'author', 'name', 'image', 'text', 'cooking_time')
        model = Recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        fields = ('id', 'user', 'author')
        model = Subscription


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'recipe')
        model = Favorite
