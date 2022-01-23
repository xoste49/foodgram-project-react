from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        author_id = instance.id
        try:
            return user.is_authenticated and Subscription.objects.filter(
                user=user, author__id=author_id).exists()
        except Exception:
            return False

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]
        read_only_fields = (settings.LOGIN_FIELD,)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        ]


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class TagCreateInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    measurement_unit = serializers.CharField(required=True)

    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientsCreateInRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        if value < 0:
            raise ValidationError(
                'Количество ингредиента не может отрицательным')
        return value

    class Meta:
        fields = ('recipe', 'id', 'amount')
        model = RecipeIngredient
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['recipe', 'id'],
                message='Ингредиенты дублируются!'
            )
        ]


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(many=False)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField('get_image_url')
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    def get_ingredients(self, instance):
        return RecipeIngredientsSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(),
            many=True
        ).data

    @staticmethod
    def get_image_url(obj):
        return obj.image.url

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text',
            'cooking_time')
        model = Recipe


def create_update_recipe(validated_data, instance=None):
    ingredients = validated_data.pop('ingredients', None)
    tags = validated_data.pop('tags', None)
    if instance is None:
        instance = Recipe.objects.create(**validated_data)
    if tags is not None:
        instance.tags.set(tags)
    if ingredients is not None:
        instance.ingredients.clear()
        create_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)
    return instance


class RecipeCreateUploadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = IngredientsCreateInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        validators=[UniqueValidator(queryset=Tag.objects.all())])
    image = Base64ImageField()

    def validate_cooking_time(self, value):
        if value < 0:
            raise ValidationError('Значение не может быть меньше нуля')
        return value

    @transaction.atomic
    def create(self, validated_data):
        return create_update_recipe(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(
            create_update_recipe(
                validated_data, instance
            ), validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientsSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(), many=True
        ).data
        return representation

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time')
        model = Recipe


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'author')
        model = Subscription
        read_only_fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return CustomUserSerializer(instance.author, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Favorite
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ShoppingCart
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]
