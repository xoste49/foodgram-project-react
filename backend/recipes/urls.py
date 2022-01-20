from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet, CustomUserViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='Recipe')
router.register('tags', TagViewSet, basename='Tag')
router.register('ingredients', IngredientViewSet, basename='Ingredient')

# http://localhost/api/users/subscriptions/
#router.register(r'users/subscriptions', SubscriptionViewSet, basename='Subscription')
# http://localhost/api/users/
# http://localhost/api/users/me/
# http://localhost/api/users/{id}/subscribe/
router.register(r'users', CustomUserViewSet, basename='Users')

# http://localhost/api/recipes/{id}/favorite/
#router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorites')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]