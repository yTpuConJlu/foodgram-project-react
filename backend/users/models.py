from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from foodgram.settings import URL_PATH_ME


class User(AbstractUser):
    """Модель пользователей."""

    """Предопределение ролей пользователей"""
    ADMIN = 'admin'
    USER = 'user'
    ROLES = (
        (ADMIN, ADMIN),
        (USER, USER),
        )
    """Поля модели User"""
    email = models.EmailField(
        max_length=150,
        verbose_name='Адрес электронной почты',
        unique=True,
        )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True
        )
    first_name = models.TextField(max_length=150)
    last_name = models.TextField(max_length=150)
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = (
            models.CheckConstraint(
                check=~models.Q(username__iexact=URL_PATH_ME),
                name='username_is_not_me'
            ),
        )


class Follow(models.Model):
    """Модель подписок.
    user - пользователь который подписывается
    author - автор на которого подписываемся
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
