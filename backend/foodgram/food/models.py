from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# class Recipe(models.Model):
#     """Модель для рецептов."""
#
#
#
#     name = models.CharField(
#         max_length=settings.NAME_FIELD_LENGTH,
#         verbose_name='Название',
#     )
#     year = models.IntegerField(
#         verbose_name='Год выпуска',
#         validators=(validate_year,)
#     )
#     description = models.TextField(
#         verbose_name='Описание',
#         blank=True)
#     genre = models.ManyToManyField(
#         Genre
#     )
#     category = models.ForeignKey(
#         Category,
#         on_delete=models.SET_NULL,
#         null=True
#     )
#
#     class Meta:
#         verbose_name = 'Произведение'
#         verbose_name_plural = 'произведение'
#         default_related_name = 'titles'
#         ordering = ('year', 'name',)
#
#     def __str__(self):
#         return self.name[:settings.OUTPUT_LENGTH]