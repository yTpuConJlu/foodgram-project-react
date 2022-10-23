from django.contrib import admin
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class BaseAdminSettings(admin.ModelAdmin):
    """Базовый класс настройки админ панели."""
    empty_value_display = '-пусто-'
    list_filter = ('author', 'name', 'tags')


class RecipeAdmin(BaseAdminSettings):
    """
    Настройка админ панели управления рецептами.
    """
    list_display = (
        'name',
        'author',
        'favorite')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    readonly_fields = ('favorite')

    def favorite(self, obj):
        return obj.in_favorite.all().count()

    favorite.short_description = 'Количество добавлений в избранное'


class IngredientAdmin(BaseAdminSettings):
    """
    Настройка админ панели управления ингредиентами.
    """
    list_display = (
        'name',
        'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(BaseAdminSettings):
    """
    Настройка админ панели управления тегами.
    """
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    """
    Настройка админ панели управления избранными рецептами.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class ShpngCartAdmin(admin.ModelAdmin):
    """
    Настройка админ панели управления корзиной покупок.
    """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user',)


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
