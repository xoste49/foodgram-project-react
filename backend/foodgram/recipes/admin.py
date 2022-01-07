from django.contrib import admin
from .models import Tag, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'cooking_time')
    search_fields = ('name',)
    list_filter = ('id', 'name', 'cooking_time')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')
    search_fields = ('name',)
    list_filter = ('id', 'name')
    empty_value_display = '-пусто-'
