from django.contrib import admin
from django.urls import include, path

from recipes.views import RecipeRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        's/<str:short_link>/', RecipeRedirectView.as_view(),
        name='recipe-redirect'
    ),
]
