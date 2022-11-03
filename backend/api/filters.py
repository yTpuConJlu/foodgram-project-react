from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework.filters import (AllValuesMultipleFilter,
                                                   BooleanFilter,
                                                   ModelChoiceFilter)

from recipes.models import Ingredient, Recipe

User = get_user_model()


class RecipeFilters(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset.all()


class IngredientFilter(FilterSet):

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
