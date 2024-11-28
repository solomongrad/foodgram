from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, SAFE_METHODS,
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter, IngredientFilter
from .permissions import ReadOnly, RecipePermission
from .serializers import (
    BaseRecipesSerializer, RecipesChangeSerializer,
    RecipesReadSerializer, IngredientsSerializer, TagSerializer
)
from recipes.models import (
    Recipe, ShoppingCart, Favorite,
    RecipeIngredient, Ingredients, Tag
)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, RecipePermission)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        serializer = self.get_serializer(
            instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        super().perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesChangeSerializer

    def add_recipe(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = BaseRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы уже удалили этот рецепт!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(model=ShoppingCart,
                                   user=request.user, pk=pk)
        return self.delete_recipe(model=ShoppingCart,
                                  user=request.user, pk=pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(model=Favorite, user=request.user, pk=pk)
        return self.delete_recipe(model=Favorite, user=request.user, pk=pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_list(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        now = datetime.now()
        format_time = now.strftime('%d-%m-%Y_%H_%M_%S')
        shopping_list = (
            f'Список покупок для {user.first_name} {user.last_name} '
            f'от {format_time}\n'
        )
        shopping_list += [
            f'· {ingredient["ingredient__name"]}'
            f' - {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
            for ingredient in ingredients
        ]
        shopping_list += '\nС любовью, ваш Foodgram!'

        filename = f'shopping_list_{user.id}_{format_time}.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk: int):
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {'message': 'Не существует такой записи'},
                status=status.HTTP_404_NOT_FOUND
            )

        scheme = request.scheme
        host = request.get_host()
        url = f'{scheme}://{host}'
        return Response(
            {'short-link': f'{url}/s/{recipe.short_link}'},
            status=status.HTTP_200_OK
        )


class RecipeRedirectView(APIView):
    """
    Вьюсет редиректа с короткой ссылки рецепта на абсолютный адрес.

    Важно: редирект идёт на адрес фронта, а не /api/!
    """

    permission_classes = [ReadOnly]

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(recipe.get_frontend_absolute_url())
