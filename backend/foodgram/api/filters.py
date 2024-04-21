from django_filters import FilterSet, filters
from rest_framework.filters import SearchFilter
from django.contrib.auth import get_user_model
from food.models import Recipe, Tag

User = get_user_model()


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method="is_favorited_filter")
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_cart_filter")

    class Meta:
        model = Recipe
        fields = ("author", "tags")

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if not value:
                return queryset.exclude(favorite__user=user)
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if not value:
                return queryset.exclude(cart__user=user)
            return queryset.filter(cart__user=user)
        return queryset
