from django_filters import FilterSet, filters
from rest_framework.filters import SearchFilter
from django.contrib.auth import get_user_model
from food.models import Recipe

User = get_user_model()


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    class Meta:
        model = Recipe
        fields = ["author", "tags"]
    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipefavorites__user=self.request.user)
        return queryset.objects.all()
    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoppinglist__user=self.request.user)
        return queryset.objects.all()
