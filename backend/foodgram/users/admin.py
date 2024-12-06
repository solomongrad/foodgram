from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .filters import UserHasRecipes, UserHasSubscribers, UserHasSubscriptions
from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'get_full_name',
        'get_avatar',
        'recipes_wrote',
        'number_of_subscriptions',
        'subscribers'
    )
    list_filter = (UserHasRecipes, UserHasSubscribers, UserHasSubscriptions)
    search_fields = ('first_name', 'last_name', 'username', 'email',)

    @display(description='Имя фамилия')
    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @display(description='Рецептов')
    def recipes_wrote(self, user):
        return user.recipes.count()

    @display(description='Подписок')
    def number_of_subscriptions(self, user):
        return user.subscribers.count()

    @display(description='Подписчиков')
    def subscribers(self, user):
        return user.authors.count()

    @display(description='Изображение')
    def get_avatar(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src={user.avatar.url} width="75" height="55"'
            )
        else:
            return ''


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
