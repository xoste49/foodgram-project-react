from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.datetime_safe import date


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField('first name', max_length=150, blank=False)
    last_name = models.CharField('last name', max_length=150, blank=False)

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        help_text='Цвет в формате HEX. Пример: #RRGGBB',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug Tag',
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user__id=user_id,
                    recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user__id=user_id,
                    recipe__pk=OuterRef('pk')
                )
            )
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_column='author',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    image = models.ImageField(upload_to='images/')
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты', through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах).',
    )
    pub_date = models.DateField(default=date.today,
                                verbose_name='Дата публикации',
                                db_index=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=1
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        # unique_together = [['recipe', 'ingredient']]


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
        unique_together = [['user', 'author']]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = [['user', 'recipe']]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
    )

    class Meta:
        unique_together = [['user', 'recipe']]
