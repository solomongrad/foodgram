from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Проверка является ли пользователь администратором."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_staff)


class IsAuthorOrReadOnly(BasePermission):
    """Проверка является ли пользователь автором."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS)


class RecipePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_authenticated and request.user.is_staff)
