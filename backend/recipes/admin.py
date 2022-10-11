from django.contrib import admin
from .models import Ingredient, Recipe, Tag


class BaseAdminSettings(admin.ModelAdmin):
    """Базовый класс кастомизации админ панели."""
    empty_value_display = '-пусто-'
    list_filter = ('author', 'name', 'tags')


class RecipeAdmin(BaseAdminSettings):
    """
    Кастомизация админ панели управления рецептами.
    """
    list_display = (
        'name',
        'author')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)


class IngredientAdmin(BaseAdminSettings):
    """
    Кастомизация админ панели управления ингредиентами.
    """
    list_display = (
        'name',
        'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(BaseAdminSettings):
    """
    Кастомизация админ панели управления тегами.
    """
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
