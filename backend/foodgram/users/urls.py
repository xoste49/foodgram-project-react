from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    GroupViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='User')
router.register(r'groups', GroupViewSet)

urlpatterns = [
    #path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]