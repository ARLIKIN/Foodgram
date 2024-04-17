from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, mixins, generics, permissions, filters

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny

from food.models import (
    Tag, Recipe,
    Favorite, Ingredient,
    ShoppingCart, Subscribe
)
from .serializers import TagsSerializer, IngredientSerializer

User = get_user_model()


class MyUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()


class TegViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('^name',)  # Todo работает только если использовать search
