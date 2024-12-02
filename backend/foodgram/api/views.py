from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from recipes.models import (
    Favorite,
    Ingredients,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .permissions import RecipePermission
from .serializers import (
    AvatarSerializer,
    BaseRecipesSerializer,
    IngredientsSerializer,
    RecipesChangeSerializer,
    RecipesReadSerializer,
    SubscriptionChangeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer
)

User = get_user_model()


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

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesChangeSerializer

    def add_recipe_to_model(self, model, user, pk):
        if model.objects.filter(author=user, recipe__id=pk).exists():
            raise ValidationError('Рецепт уже добавлен!')
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(author=user, recipe=recipe)
        return Response(BaseRecipesSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    def delete_recipe_from_model(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            raise Http404('Такого рецепта не существует.')
        object = model.objects.filter(author=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError('Вы уже удалили этот рецепт!')

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe_to_model(model=ShoppingCart,
                                            user=request.user, pk=pk)
        return self.delete_recipe_from_model(model=ShoppingCart,
                                             user=request.user, pk=pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe_to_model(model=Favorite,
                                            user=request.user,
                                            pk=pk)
        return self.delete_recipe_from_model(model=Favorite,
                                             user=request.user,
                                             pk=pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipe__author=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        now = datetime.now()
        format_time = now.strftime('%d-%m-%Y_%H_%M_%S')
        shopping_list = (
            f'Список покупок для {user.first_name} {user.last_name} '
            f'от {format_time}\n'
        )
        shopping_list += ''.join(
            f'· {ingredient["ingredient__name"]}'
            f' - {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
            for ingredient in ingredients
        )
        shopping_list += '\nС любовью, ваш Foodgram!'

        filename = f'shopping_list_{user.id}_{format_time}.txt'
        return FileResponse(shopping_list,
                            content_type='text/plain',
                            as_attachment=True,
                            filename=filename)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk: int):
        recipe = self.get_object()

        url = f'{request.scheme}://{request.get_host()}'
        return Response(
            {'short-link': f'{url}/s/{recipe.short_link}'},
            status=status.HTTP_200_OK
        )


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            data = {
                'user': user.id,
                'author': author.id
            }
            serializer = SubscriptionChangeSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscriptions_author__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get', 'put', 'patch', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        ['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        name='set_avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request, *args, **kwargs):
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                raise ValidationError('Отсутствует изображение!')

            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            avatar_data = serializer.validated_data.get('avatar')
            request.user.avatar = avatar_data
            request.user.save()

            image_url = request.build_absolute_uri(
                f'/media/users/{avatar_data.name}'
            )
            return response.Response(
                {'avatar': str(image_url)}, status=status.HTTP_200_OK
            )
        self.request.user.avatar.delete()
        self.request.user.avatar = None
        self.request.user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
