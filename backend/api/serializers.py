from djoser.serializers import UserSerializer
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from food.models import (
    Ingredient, Tag,
    Recipe, RecipeIngredient
)
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(UserSerializer):
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
        return request_user.subscribed.filter(sub_user=user).exists()


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'name', 'cooking_time'
        )


class UserSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_recipes_count(self, user):
        return user.recipes.all().count()

    def get_recipes(self, user):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeMiniSerializer(
            recipes, many=True, context=self.context
        )
        return serializer.data


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
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )
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


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = WriteRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField(represent_in_base64=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        if 'image' in data:
            if not data['image']:
                raise serializers.ValidationError(
                    'В запросе обязательно должна быть картинка'
                )
        if 'ingredients' not in data or not data['ingredients']:
            raise ValidationError(
                'В запросе обязательно должны быть ингридиенты'
            )
        if 'tags' not in data or not data['tags']:
            raise ValidationError(
                'В запросе обязательно должны быть тэги'
            )
        for tag in data['tags']:
            if data['tags'].count(tag) > 1:
                raise ValidationError(
                    'Тэг дублируется'
                )
        for ingredient in data['ingredients']:
            if data['ingredients'].count(ingredient) > 1:
                raise ValidationError(
                    'Ингридиент дублируется'
                )
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
        return super().validate(data)

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError(
                'Время приготовления минимум 1 минута'
            )
        return cooking_time

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data
        )
        self.create_recipe_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.tags.set(tags_data)
        self.create_recipe_ingredients(ingredients_data, recipe)
        return recipe

    def create_recipe_ingredients(self, ingredients_data, recipe):
        for ingredient in ingredients_data:
            RecipeIngredient.objects.bulk_create(
                [RecipeIngredient(
                    recipe=recipe, ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )]
            )

    def to_representation(self, recipe):
        return ReadRecipeSerializer(recipe, context=self.context).data
