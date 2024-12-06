from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_TAG,
    MIN_COOKING_TIME,
    MIN_RECIPE_INGREDIENT_AMOUNT
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_TAG,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_TAG,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=256,
                            verbose_name='Название')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
        ),
        verbose_name='Время (мин)'
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Время создания рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            MIN_RECIPE_INGREDIENT_AMOUNT,
            message=(
                'Слишком мало ингридиента. Минимум: '
                f'{MIN_RECIPE_INGREDIENT_AMOUNT}.'
            )
        ),),
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('-amount',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient'
            ),
        )


class BaseCartOrFavorite(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_%(class)s_unique_recipe',
            ),
        )


class Favorite(BaseCartOrFavorite):

    class Meta(BaseCartOrFavorite.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'


class ShoppingCart(BaseCartOrFavorite):

    class Meta(BaseCartOrFavorite.Meta):
        verbose_name = 'Рецепт из корзины'
        verbose_name_plural = 'Рецепты из корзины'
        default_related_name = 'shopping_carts'
