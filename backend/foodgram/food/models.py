from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель для тэгов."""
    name = models.CharField(verbose_name='Название', max_length=200)
    color = models.CharField(verbose_name='Цвет', max_length=7)
    slug = models.CharField(verbose_name='Слаг', max_length=200)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'тэг'
        default_related_name = 'tags'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(verbose_name='Название', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'ингридиент'
        default_related_name = 'ingredients'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество')


class Recipe(models.Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    name = models.CharField(verbose_name='Название', max_length=200)
    image = models.ImageField(
        upload_to='foodgram/images/',
        null=True,
        default=None,
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(verbose_name='Текст', max_length=200)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    tag = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепт'
        default_related_name = 'recipe'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class Favorite(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранное'
        default_related_name = 'favorites'
        ordering = ('user',)

    def __str__(self):
        return self.user[:settings.OUTPUT_LENGTH]


class ShoppingCart(models.Model):
    """Модель для коризны."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'корзина'
        default_related_name = 'shopping_cart'
        ordering = ('user',)

    def __str__(self):
        return self.user[:settings.OUTPUT_LENGTH]


class Subscribe(models.Model):
    """Модель для подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Subscribed'
    )
    sub_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Subscribe'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'подписки'
        ordering = ('user',)

    def __str__(self):
        return self.user[:settings.OUTPUT_LENGTH]
