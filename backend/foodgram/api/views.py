from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, mixins, generics, permissions, filters, \
    status

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from food.models import (
    Tag, Recipe,
    Favorite, Ingredient,
    ShoppingCart, Subscribe
)
from rest_framework.response import Response

from .serializers import (
    TagsSerializer,
    IngredientSerializer,
    WriteRecipeSerializer,
    ReadRecipeSerializer,
    UserSubscribeSerializer,
    RecipeMiniSerializer
)
from .filters import IngredientFilter, RecipesFilter
from .permissions import IsAuthorOrReadOnly

User = get_user_model()


class MyUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(subscribe__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        pagination_class=None
    )
    def subscribe(self, request, id=None):
        if not User.objects.filter(pk=id).exists():
            return Response(
                'Пользователь не существует',
                status=status.HTTP_404_NOT_FOUND
            )
        user = User.objects.get(pk=id)
        if Subscribe.objects.filter(user=request.user, sub_user=user):
            return Response(
                'Попытка создания дублирующей подписки',
                status=status.HTTP_400_BAD_REQUEST
            )
        if user == request.user:
            return Response(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.create(user=request.user, sub_user=user)
        serializer = UserSubscribeSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TegViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk) -> Response:
        """Добавляет или удаляет рецепт в избранное"""

    @favorite.mapping.post
    def favorite_add(self, request, pk=None):
        recipe = Recipe.objects.filter(id=pk).first()
        if not recipe:
            return Response(
                'Рецепт не существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(id=pk)
        if Favorite.objects.filter(user=request.user, recipe=recipe):
            return Response(
                'Попытка повторного добавления рецепта в избранное',
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        recipe = Recipe.objects.filter(id=pk).first()
        if not recipe:
            return Response(
                'Рецепт не существует',
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = Recipe.objects.get(id=pk)
        favorite_instance = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not favorite_instance:
            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_instance.delete()
        return Response('Рецепт удален из избранного')

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
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
