from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Recipe, Tag, Ingredient, Subscription
from .pagination import LimitPagination
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer, \
    SubscriptionSerializer, CustomUserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.order_by("pk").all()
    pagination_class = LimitPagination


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        if tags is not None:
            queryset = queryset.filter(tags__slug__in=tags)
        author = self.request.query_params.get('author')
        if author is not None:
            queryset = queryset.filter(author__id=author)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = [AllowAny]


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def get_queryset(self):
        queryset = Subscription.objects.all().filter(user=self.request.user)
        print(queryset)
        return queryset
