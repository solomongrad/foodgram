from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet,
    MyUserViewSet,
    RecipeViewSet,
    TagsViewSet
)

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', MyUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
