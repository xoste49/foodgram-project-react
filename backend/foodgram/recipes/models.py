from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Тег
    Все поля обязательны для заполнения и уникальны
    """
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=100,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        help_text='Цвет в формате HEX. Пример: #RRGGBB',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug Tag',
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Рецепт
    Автор публикации (пользователь).
    Название.
    Картинка.
    Текстовое описание.
    Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
    Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
    Время приготовления в минутах.
    Все поля обязательны для заполнения.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_column='author',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=100,
    )
    image = models.ImageField(upload_to='images/')
    text = models.CharField(
        verbose_name='Описание рецепта',
        blank=True,
        null=False,
        max_length=3000,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах.',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    user — ссылка на объект пользователя, который подписывается.
    author — ссылка на объект пользователя, на которого подписываются,
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
