from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, username, first_name, last_name,
                    password, **extra_fields):
        user = self.model(
            email=email, username=username, first_name=first_name,
            last_name=last_name, password=password, **extra_fields
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name,
                         password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, username=username,
                                first_name=first_name, last_name=last_name,
                                password=password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    first_name = models.CharField(verbose_name='имя пользователя',
                                  max_length=150)
    last_name = models.CharField(verbose_name='фамилия пользователя',
                                 max_length=150)
    username = models.CharField(verbose_name='никнейм пользователя',
                                validators=[UnicodeUsernameValidator()],
                                max_length=150, unique=True)
    email = models.EmailField(verbose_name='электронная почта пользователя',
                              max_length=254, unique=True)
    is_staff = models.BooleanField(
        verbose_name='Является админом',
        default=False,
        help_text=(
            'Указывает, может ли пользователь войти на '
            'страницу администратора.'
        )
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        blank=True,
        help_text=(
            'Аватар пользователя, по умолчанию загружается другая картинка'
        )
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)


class Subscribtion(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author',
        verbose_name='Автор на которого подписан'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user',
        verbose_name='Подписчик'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Время подписки'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_subscription'
            )
        ]
