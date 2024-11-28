from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (AvatarSerializer,
                             UserSerializer,
                             SubscribtionSerializer,
                             SubscriptionChangeSerializer)
from .models import Subscribtion

User = get_user_model()


class CustomUserViewSet(UserViewSet):
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
        # data: dict = self.get_data(request=request, id=id)
        # serializer = SubscriptionChangeSerializer(
        #     data={key: obj.id for key, obj in data.items()},
        #     context={'request': request}
        # )
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
            # Subscribtion.objects.create(user=user, author=author)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Subscribtion,
                                         user=user,
                                         author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionSerializer(pages,
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
                return response.Response(
                    {'avatar': 'Отсутствует изображение!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        self.request.user.avatar = None
        self.request.user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
