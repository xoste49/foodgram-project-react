from django.db import models


class Recipe(models.Model):
    """
    Рецепт
    Рецепт должен описываться такими полями:
    Автор публикации (пользователь).
    Название.
    Картинка.
    Текстовое описание.
    Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
    Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
    Время приготовления в минутах.
    Все поля обязательны для заполнения.
    """
    # author
    title = models.CharField(
        verbose_name='Название рецепта',
        default='',
        max_length=100,
    )
    # image
    description = models.CharField(
        verbose_name='Описание рецепта',
        blank=True,
        null=False,
        default='',
        max_length=3000,
    )
    # ingredients
    # tag
    # cookingtime


class Tag(models.Model):
    """
    Тег
    Тег должен описываться такими полями:
    Название
    Цветовой HEX-код (например, #49B64E)
    Slug
    Все поля обязательны для заполнения и уникальны
    """
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=100,
    )
    #color
    #slug
    pass