from rest_framework import viewsets

from django.contrib.auth import get_user_model

from backend.foodgram.food.models import (
    Tag, Recipe,
    Favorite, Ingredient,
    ShoppingCart, Subscribe
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()


class TegViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
