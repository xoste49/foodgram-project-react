from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='Recipe')
router.register('tags', TagViewSet, basename='Tag')
router.register('ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'users', CustomUserViewSet, basename='Users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]
