from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
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
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    BaseRecipesSerializer,
    IngredientsSerializer,
    RecipesChangeSerializer,
    RecipesReadSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer
)
from .shopping_list_def import form_shopping_list

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
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
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
            raise ValidationError('Этот рецепт уже был добавлен ранее!')
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(author=user, recipe=recipe)
        return Response(BaseRecipesSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    def delete_recipe_from_model(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            raise ValidationError(f'Рецепта с id={pk} не существует.')
        get_object_or_404(model, author=user, recipe__id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            recipe__shopping_carts__author=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        recipe_names = [
            shopping_cart.recipe.name
            for shopping_cart in ShoppingCart.objects.filter(author=user)
        ]
        shopping_list = form_shopping_list(user=user,
                                           ingredients=ingredients,
                                           recipe_names=recipe_names)
        filename = (f'shopping_list_{user.id}_'
                    f'{datetime.now().strftime("%d-%m-%Y_%H_%M_%S")}.txt')
        return FileResponse(shopping_list,
                            content_type='text/plain',
                            as_attachment=True,
                            filename=filename)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk: int):
        get_object_or_404(Recipe, id=pk)
        return Response(
            {'short-link': request.build_absolute_uri(
                location=None
            ).replace(
                request.get_full_path(), ''
            ) + reverse('recipe:recipe-redirect', args=(pk,))},
            status=status.HTTP_200_OK
        )


class UserViewSet(DjoserUserViewSet):
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
        if author == user:
            raise ValidationError('Подписаться на самого себя невозможно.')

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            Subscription.objects.create(user=user, author=author)
        except IntegrityError:
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
            )
        # ревьюверу: я искренне не имею ни малейшего понятия, как вернуть
        # такой же ответ без сериалайзера, единственное, что приходит в голову,
        # это сделать это вручную, но это не вариант.
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribers__user=user)
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
