from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

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
    readonly_fields = (
        'recipes_wrote',
        'number_of_subscriptions',
        'subscribers'
    )
    list_filter = ('first_name',)
    search_fields = ('first_name', 'email', 'first_name',)

    @display(description='Имя фамилия')
    def get_full_name(self, user):
        return user.__str__()

    @display(description='Количество написанных рецептов')
    def recipes_wrote(self, user):
        return user.recipes.count()

    @display(description='Количество подписок')
    def number_of_subscriptions(self, user):
        return user.subscriptions.count()

    @display(description='Количество подписчиков')
    def subscribers(self, user):
        return user.subscribers.count()

    @display(description='Изображение')
    def get_avatar(self, user):
        try:
            return mark_safe(
                f'<img src={user.avatar.url} width="75" height="55"'
            )
        except ValueError:
            return 'Изображение отсутствует'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
