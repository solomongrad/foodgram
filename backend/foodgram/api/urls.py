from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, IngredientsViewSet, TagsViewSet
from users.views import CustomUserViewSet

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]