from django.contrib import admin


class BaseHasRecipes(admin.SimpleListFilter):
    title = ''
    parameter_name = ''

    def lookups(self, request, model_admin):
        return [
            ('yes', 'да'),
            ('no', 'нет')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(recipes=None)
        if self.value() == 'no':
            return queryset.filter(recipes=None)


class UserHasRecipes(BaseHasRecipes):
    title = 'Есть рецепты'
    parameter_name = 'has_recipe'


class UserHasSubscriptions(BaseHasRecipes):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(subscribers=None)
        if self.value() == 'no':
            return queryset.filter(subscribers=None)


class UserHasSubscribers(BaseHasRecipes):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(authors=None)
        if self.value() == 'no':
            return queryset.filter(authors=None)
