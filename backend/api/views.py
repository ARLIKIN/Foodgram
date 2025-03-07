import io

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from food.models import (
    Tag, Recipe,
    Favorite, Ingredient,
    ShoppingCart, Subscribe
)
from rest_framework.response import Response

from .paginations import LimitPageNumberPagination
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
from .create_file import create_file_str

User = get_user_model()


class UserViewSet(UserViewSet):

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
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

    @action(detail=True, methods=[])
    def subscribe(self, request, pk) -> Response:
        """Добавляет или удаляет рецепт в корзину"""

    @subscribe.mapping.post
    def subscribe_add(self, request, id=None):
        user = User.objects.filter(pk=id).first()
        if not user:
            return Response(
                {'errors': 'Пользователь не существует'},
                status=status.HTTP_404_NOT_FOUND
            )
        if Subscribe.objects.filter(user=request.user, sub_user=user):
            return Response(
                {'errors': 'Попытка создания дублирующей подписки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user == request.user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.create(user=request.user, sub_user=user)
        serializer = UserSubscribeSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id=None):
        user = User.objects.filter(pk=id).first()
        if not user:
            return Response(
                {'errors': 'Пользователь не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

        del_count, _ = Subscribe.objects.filter(
            user=request.user, sub_user=user
        ).delete()
        if del_count:
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TegViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return Recipe.recipe_manager.annotate_recipe(self.request)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def create_favorite_shopping_cart(self, request, model, pk):
        recipe = Recipe.objects.filter(id=pk).first()
        if not recipe:
            return Response(
                {'errors': 'Рецепт не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(user=request.user, recipe=recipe):
            return Response(
                {'errors': 'Попытка повторного добавления рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy_favorite_shopping_cart(self, request, model, pk):
        recipe = Recipe.objects.filter(id=pk).first()
        if not recipe:
            return Response(
                {'errors': 'Рецепт не существует'},
                status=status.HTTP_404_NOT_FOUND
            )
        instance = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not instance:
            return Response(
                {'errors': 'Рецепта нет'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(
            'Рецепт удален',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True)
    def favorite(self, request, pk) -> Response:
        """Добавляет или удаляет рецепт в избранное"""

    @favorite.mapping.post
    def favorite_add(self, request, pk=None):
        return self.create_favorite_shopping_cart(request, Favorite, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.destroy_favorite_shopping_cart(request, Favorite, pk)

    @action(
        detail=False,
        methods=['get']
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.shoppingcarts.all()
        file = create_file_str(shopping_cart)
        file_object = io.BytesIO()
        file_object.write(file.encode())
        file_object.seek(0)
        return FileResponse(file_object, filename='shopping_cart.txt')

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk) -> Response:
        """Добавляет или удаляет рецепт в корзину"""

    @shopping_cart.mapping.post
    def shopping_add(self, request, pk=None):
        return self.create_favorite_shopping_cart(request, ShoppingCart, pk)

    @shopping_cart.mapping.delete
    def shopping_delete(self, request, pk=None):
        return self.destroy_favorite_shopping_cart(request, ShoppingCart, pk)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
