from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django.http import HttpResponse
from django.views.generic import detail
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Recipe, Tag, Ingredient, Favorite, Subscription, \
    RecipeIngredient, ShoppingCart
from .pagination import LimitPagination
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer, \
    SubscriptionSerializer, FavoriteSerializer, SubscribeSerializer, \
    CustomUserSerializer, RecipeCreateUploadSerializer, \
    RecipeMinifiedSerializer, ShoppingCartSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.order_by("pk").all()
    pagination_class = LimitPagination

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff and not user.is_anonymous:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        serializer = SubscribeSerializer(data=request.data)
        user = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            if self.request.user == user:
                print('Вы пытаетесь подписаться на себя')
                raise ValidationError(
                    {'errors': 'Вы пытаетесь подписаться на себя'},
                    status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=self.request.user,
                                           author=user).exists():
                print('Вы уже подписаны на пользователя')
                raise ValidationError(
                    {'errors': 'Вы уже подписаны на пользователя'},
                    status.HTTP_400_BAD_REQUEST
                )
            if serializer.is_valid():
                print('Подписка успешно создана')
                print(CustomUserSerializer(user))
                print('self.request', self.request.data)
                print('serializer', serializer)
                serializer2 = self.get_serializer(user, many=False)
                serializer.save(user=self.request.user, author=user)
                return Response(serializer2.data)
        if self.request.method == 'DELETE':
            obj = Subscription.objects.filter(user=self.request.user,
                                              author=user)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"errors": "Вы не подписаны на автора"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('errors')

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscriber__user=self.request.user).all()
        context = self.get_serializer_context()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(
            page,
            context=context,
            many=True
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUploadSerializer
        elif self.action in ('shopping_cart', 'favorite'):
            return RecipeMinifiedSerializer
        else:
            return RecipeSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update'):
            permission_classes = [IsAuthenticated]
        elif self.action in ('shopping_cart', 'favorite'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects
        queryset = queryset.add_user_annotations(user.id)
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(is_in_shopping_cart=True)
        if len(tags) != 0:
            queryset = queryset.filter(tags__slug__in=tags)
        if author is not None:
            queryset = queryset.filter(author__id=author)
        return queryset.order_by('-pub_date').all()

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(data=request.data)
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if Favorite.objects.filter(user=self.request.user,
                                       recipe=recipe).exists():
                raise ValidationError(
                    {'errors': 'Рецепт уже есть в избранном'},
                    status.HTTP_400_BAD_REQUEST
                )
            if serializer.is_valid():
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(RecipeMinifiedSerializer(recipe).data,
                                status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            obj = Favorite.objects.filter(user=self.request.user,
                                          recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Вы не добавляли рецепт в избранное"},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response('errors')

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = ShoppingCart.objects.filter(user=self.request.user, recipe=recipe)
        if self.request.method == 'POST':
            serializer = ShoppingCartSerializer(data=request.data)
            if obj.exists():
                raise ValidationError(
                    {'errors': 'Рецепт уже есть в списке покупок'},
                    status.HTTP_400_BAD_REQUEST
                )
            if serializer.is_valid():
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(RecipeMinifiedSerializer(recipe).data,
                                status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Вы не добавляли рецепт в список покупок"},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response('errors')

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        items = RecipeIngredient.objects.select_related('recipe', 'ingredient')
        items = items.filter(recipe__shopping_carts__user=request.user)
        items = items.values('ingredient__name',
                             'ingredient__measurement_unit').annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount')).order_by('-total')

        text = '\n'.join(
            f"{item['name']} - {item['total']} {item['units']}" for item in
            items)
        filename = 'shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = [AllowAny]

    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    search_fields = ['name']

    http_method_names = ['get']

    def get_queryset(self):
        queryset = Ingredient.objects
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset.all()


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    http_method_names = ['post', 'delete']

    def get_queryset(self):
        return Favorite.objects.all()

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        if Favorite.objects.filter(user=self.request.user,
                                   recipe=recipe).exists():
            raise ValidationError(
                {'errors': 'Рецепт уже есть в избранном'},
                status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            print('Рецепт успешно добавлен в избранное')
            serializer.save(user=self.request.user, recipe=recipe)
            return Response('Ничего не возвращаю',
                            status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
