from django.contrib import admin
from django.contrib.admin import display
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredients,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    fields = ('recipe', 'ingredient', 'amount', 'get_measurement_unit')
    readonly_fields = ('get_measurement_unit',)

    @display(description='Единица измерения')
    def get_measurement_unit(self, recipe_ingredient):
        return recipe_ingredient.ingredient.measurement_unit


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'get_tags',
        'added_in_favorites',
        'get_ingredients',
        'get_image'
    )
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'tags',)
    search_fields = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientAdmin,)

    @display(description='В избранных')
    def added_in_favorites(self, recipe):
        return recipe.favorites.count()

    @display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe('<br>'.join(
            f'{recipe_ingredient.ingredient} - {recipe_ingredient.amount}'
            f'{recipe_ingredient.ingredient.measurement_unit}'
            for recipe_ingredient in recipe.recipe_ingredients.all()
        ))

    @display(description='Изображение')
    def get_image(self, recipe):
        return mark_safe(f'<img src={recipe.image.url} width="75" height="55"')

    @display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe('<br>'.join(f'{tag}' for tag in
                         recipe.tags.filter(recipes=recipe)))


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'added_in_recipe'
    )
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit',)

    @display(description='Рецептов')
    def added_in_recipe(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'recipes_with_this_tag',
    )

    @display(description='Рецептов')
    def recipes_with_this_tag(self, tag):
        return tag.recipes.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)
