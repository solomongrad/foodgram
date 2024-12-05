from django.shortcuts import redirect
from rest_framework.serializers import ValidationError

from .models import Recipe


def get_redirect_short_link(request, pk):
    if Recipe.objects.filter(id=pk).exists():
        return redirect(f'/recipes/{pk}/')
    raise ValidationError(f'Рецепта с id={pk} не существует.')
