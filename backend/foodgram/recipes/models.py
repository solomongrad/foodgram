from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import MIN_COOKING_TIME, MIN_INGREDIENTS_PER_RECIPE
from core.utils import generate_short_link

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=256,
                            verbose_name='Название')
    image = models.ImageField(upload_to='posts/',
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
        verbose_name='Время приготовления'
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка', default=generate_short_link,
        unique=True, max_length=6
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='время создания рецепта')

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
        default=MIN_INGREDIENTS_PER_RECIPE,
        validators=(MinValueValidator(
            MIN_INGREDIENTS_PER_RECIPE,
            message=(
                f'Мин. количество ингридиентов {MIN_INGREDIENTS_PER_RECIPE}'
            )
        ),),
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'Соотношение ингредиента и рецепта'
        verbose_name_plural = 'Соотношение ингредиентов и рецепта'
        ordering = ('-id',)
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
        verbose_name='владелец'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique recipe',
            ),
        )


class Favorite(BaseCartOrFavorite):

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite_recipes'


class ShoppingCart(BaseCartOrFavorite):

    class Meta:
        verbose_name = 'Рецепт из корзины'
        verbose_name_plural = 'Рецепты из корзины'
        default_related_name = 'shopping_cart_recipe'
