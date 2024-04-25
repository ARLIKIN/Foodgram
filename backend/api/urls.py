from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    UserViewSet, TegViewSet,
    IngredientsViewSet, RecipeViewSet,
)

router_v1 = SimpleRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'tags', TegViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
