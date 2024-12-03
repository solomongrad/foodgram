from django.urls import path

from .views import get_redirect_short_link

app_name = 'recipe'

urlpatterns = [
    path(
        's/<int:short_link>/', get_redirect_short_link,
        name='recipe-redirect'
    ),
]
