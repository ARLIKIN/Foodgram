from djoser.views import UserViewSet
from rest_framework import viewsets, mixins, generics, permissions

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny

from food.models import (
    Tag, Recipe,
    Favorite, Ingredient,
    ShoppingCart, Subscribe
)

User = get_user_model()


class MyUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()


class TegViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
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
