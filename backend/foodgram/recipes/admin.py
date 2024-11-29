from django.contrib import admin
from django.contrib.admin import display

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
    list_display = ('name', 'id', 'author', 'recipe_favorite')
    readonly_fields = ('recipe_favorite',)
    list_filter = ('author', 'name', 'tags',)

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
