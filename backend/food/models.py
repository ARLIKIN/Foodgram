from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseCartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        unique_together = ('user', 'recipe')
        ordering = ('user',)

    def __str__(self):
        return self.user[:settings.OUTPUT_LENGTH]


class BaseName(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class Tag(BaseName):
    """Модель для тэгов."""
    color = models.CharField(verbose_name='Цвет', max_length=7)
    slug = models.CharField(verbose_name='Слаг', max_length=200)

    class Meta(BaseName.Meta):
        verbose_name = 'Тэг'
        verbose_name_plural = 'тэг'


class Ingredient(BaseName):
    """Модель для ингредиентов."""
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения', max_length=200
    )

    class Meta(BaseName.Meta):
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'ингридиент'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        default_related_name = 'recipe_ingredients'
        unique_together = ('recipe', 'ingredient')


class Recipe(BaseName):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
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
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )

    class Meta(BaseName.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепт'
        ordering = ('pub_date',)


class Favorite(BaseCartItem):
    """Модель для избранных рецептов."""

    class Meta(BaseCartItem.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранное'


class ShoppingCart(BaseCartItem):
    """Модель для коризны."""

    class Meta(BaseCartItem.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'корзина'


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
        unique_together = ('user', 'sub_user')
        ordering = ('user',)

    def __str__(self):
        return self.user[:settings.OUTPUT_LENGTH]
