import base64

from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers
from food.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, user):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return user.subscribed.filter(sub_user=request_user).exists()


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'name', 'image',
            'is_favorited', 'is_in_shopping_cart',
            'text', 'cooking_time'
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
           'id', 'name', 'measurement_unit',
           amount=F('recipe_ingredients__amount')
        )

    def get_is_favorited(self, recipe):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request_user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request_user, recipe=recipe
        ).exists()


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = WriteRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context.get("request").user, **validated_data
        )
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        pass

    def to_representation(self, recipe):
        return ReadRecipeSerializer(recipe, context=self.context).data
