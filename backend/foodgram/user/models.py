from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email', unique=True, max_length=254
    )
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)
    password = models.CharField(verbose_name='Пароль', max_length=150)
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        validators=(validate_username,),
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta(AbstractUser.Meta):
        ordering = ('id',)
        default_related_name = 'users'
