from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    first_name = models.CharField(verbose_name='Имя',
                                  max_length=150)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=150)
    username = models.CharField(verbose_name='Никнейм',
                                validators=[UnicodeUsernameValidator()],
                                max_length=150, unique=True)
    email = models.EmailField(verbose_name='Почта',
                              max_length=254, unique=True)
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        blank=True,
        help_text=('Аватар')
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)


class Subscription(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_subscription'
            )
        ]
