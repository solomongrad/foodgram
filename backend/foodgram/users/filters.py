from django.contrib import admin


class UserHasRecipes(admin.SimpleListFilter):
    title = 'есть рецепты'
    parameter_name = 'has_recipe'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'пользователи с рецептами'),
            ('no', 'пользователи без рецептов')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(recipes=None)
        if self.value() == 'no':
            return queryset.filter(recipes=None)

class UserHasSubscriptions(admin.SimpleListFilter):
    title = 'есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'пользователи с подписками'),
            ('no', 'пользователи без подписок')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(subscribers=None)
        if self.value() == 'no':
            return queryset.filter(subscribers=None)

class UserHasSubscribers(admin.SimpleListFilter):
    title = 'есть подписчики'
    parameter_name = 'has_subscribers'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'пользователи с подписчиками'),
            ('no', 'пользователи без подписчиков')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(authors=None)
        if self.value() == 'no':
            return queryset.filter(authors=None)
