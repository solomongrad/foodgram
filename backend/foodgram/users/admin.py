from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
        'avatar',
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
    search_fields = ('first_name', 'email',)

    @display(description='Количество написанных рецептов')
    def recipes_wrote(self, user):
        return user.recipes.count()

    @display(description='Количество подписок')
    def number_of_subscriptions(self, user):
        return user.subscriptions_user.count()

    @display(description='Количество подписчиков')
    def subscribers(self, user):
        return user.subscriptions_auhtor.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
