from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet, SubscriptionViewSet, CustomUserViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='Recipe')
router.register('tags', TagViewSet, basename='Tag')
router.register('ingredients', IngredientViewSet, basename='Ingredient')
# http://localhost/api/users/{id}/subscribe/
router.register(r'users/(?P<user_id>\d+)/subscribe', SubscriptionViewSet, basename='Subscribe')
# http://localhost/api/users/subscriptions/
router.register(r'users/subscriptions', SubscriptionViewSet, basename='Subscription')
router.register(r'users', CustomUserViewSet, basename='Users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]