from django.contrib import admin

from .models import Tag, Recipe, Ingredient, ShoppingCart, Favorite


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = list_display


@admin.register(Favorite)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = list_display


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('count_in_favorite',)
    list_display = (
        'name', 'author', 'image', 'text',
        'cooking_time', 'count_in_favorite'
    )
    list_filter = ('tags', 'author', 'name')

    @admin.display(description='Счетчик в избранном')
    def count_in_favorite(self, recipe):
        return recipe.favoriterecipes.count()
