from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    MyUserViewSet, TegViewSet,
    IngredientsViewSet, RecipeViewSet,
    SubscribeViewSet, FavoriteViewSet,
    ShoppingCartViewSet
)

router_v1 = SimpleRouter()
router_v1.register(r'users', MyUserViewSet, basename='users')
router_v1.register(r'tags', TegViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)


# recipes = [
#     path(
#         r'download_shopping_cart/',
#         ShoppingCartViewSet.as_view(),
#         name='download'
#     ),
#     path(
#         r'(?P<id>\d+)/shopping_cart/',
#         ShoppingCartViewSet.as_view(),
#         name='shopp_update'
#     ),
#     path(
#         r'(?P<id>\d+)/favorite/',
#         FavoriteViewSet.as_view(),
#         name='favorite'
#     ),
# ]

# users = [
#     path(r'subscriptions/', SubscribeViewSet.as_view(), name='subscriptions'),
#     path(
#         r'(?P<id>\d+)/subscriptions/',
#         SubscribeViewSet.as_view(),
#         name='subscriptions_update'
#     ),
# ]


urlpatterns = [
    # path(r'recipes/', include(recipes)),
    # path(r'users/', include(users)),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]

