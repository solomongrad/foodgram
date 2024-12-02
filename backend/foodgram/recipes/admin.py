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

    @display(description='Количество в избранных')
    def added_in_favorites(self, recipe):
        return recipe.favorites.count()

    @display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe(recipe.ingredients)

    @display(description='Изображение')
    def get_image(self, recipe):
        return mark_safe(recipe.image)

    @display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe(recipe.tags)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'added_in_recipe'
    )
    readonly_fields = ('added_in_recipe',)
    list_filter = ('measurement_unit',)

    @display(description='Количество рецептов с этим ингредиентом')
    def added_in_recipe(self, ingredient):
        return ingredient.recipe.count()

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'recipes_with_this_tag',
    )
    readonly_fields = ('recipes_with_this_tag',)

    @display(description='Количество рецептов с этим тегом')
    def recipes_with_this_tag(self, tag):
        return tag.recipe.count()

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
