from django.contrib import admin
from core.constants import FILTERS_LOOKUPS


class BaseHasRecipes(admin.SimpleListFilter):
    title = ''
    parameter_name = ''
    filter_arg = dict()

    def lookups(self, request, model_admin):
        return FILTERS_LOOKUPS

    def queryset(self, request, queryset):
        if self.value():
            return (queryset.exclude if self.value() == 'yes'
                    else queryset.filter)(**self.filter_arg)
        return queryset


class UserHasRecipes(BaseHasRecipes):
    title = 'Есть рецепты'
    parameter_name = 'has_recipe'
    filter_arg = {'recipes': None}


class UserHasSubscriptions(BaseHasRecipes):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    filter_arg = {'subscribers': None}


class UserHasSubscribers(BaseHasRecipes):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    filter_arg = {'authors': None}
