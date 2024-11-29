from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

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
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='posts/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipe',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(1000)
        )
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка', default=generate_short_link,
        max_length=6
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def get_frontend_absolute_url(self):
        return '/recipes/{pk}/'.format(pk=self.pk)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient')
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient')
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(
            1, message='Мин. количество ингридиентов 1'
        ),),
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient'
            ),
        )


class RecipeTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Favorite(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
        verbose_name='владелец избранного'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique recipe in favorite',
            ),
        )


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='владелец корзины покупок'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт из корзины'
        verbose_name_plural = 'Рецепты из корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique recipe in shopping cart',
            ),
        )
