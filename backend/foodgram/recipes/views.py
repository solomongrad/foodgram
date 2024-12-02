from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView

from .models import Recipe


class RecipeRedirectView(APIView):
    """
    Вьюсет редиректа с короткой ссылки рецепта на абсолютный адрес.
    """

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect('/recipes/{pk}/'.format(pk=recipe.pk))
