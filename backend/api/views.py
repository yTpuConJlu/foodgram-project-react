from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.db.models import F, Sum
from recipes.models import ShpngCart
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from recipes.models import Favorite, Ingredient, IngredientRecipe, Recipe, Tag
from users.models import Follow
from .filters import RecipeFilters
from .pagination import CustomPagination
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          FollowSerializer,
                          FollowListSerializer,
                          SpngCartSerializer,
                          RecipeSerializer,
                          TagSerializer,
                          UserSerializer,
                          FollowCreateSerializer
                          )

User = get_user_model()


class UsersViewSet(UserViewSet):
    pagination_class = CustomPagination
    queryset = User.objects.all()

    @action(['get'],
            detail=False,
            permission_classes=(IsAuthenticated,)
            )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, id):
        author_id = get_object_or_404(User, id=id).id
        user_id = request.user.id
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={
                    'user': user_id,
                    'author': author_id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = get_object_or_404(
            Follow,
            author=get_object_or_404(User, pk=id),
            user=request.user
            )
        self.perform_destroy(follow)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):

        users_subscriptions = User.objects.filter(following__user=request.user)
        serializer = FollowListSerializer(
            users_subscriptions,
            many=True,
            context={
                "request": request
            }
        )
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    filter_backends = DjangoFilterBackend
    filter_class = RecipeFilters
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def fav_shpng_methods(request, pk, model, errors):
        if request.method == 'POST':
            if model.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response(
                    {'errors': errors['recipe_alrdy_in']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=request.user, recipe=recipe)
            serializer = SpngCartSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = model.objects.filter(user=request.user, recipe__id=pk)
        if recipe.exists():
            recipe.delete()
            return Response(
                {'msg': 'Успешно удалено'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'error': errors['recipe_not_in_yet']},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
        )
    def shopping_cart(self, request, pk):
        return self.fav_shpng_methods(request, pk, ShpngCart, {
            'recipe_alrdy_in': 'Рецепт уже добавлен.',
            'recipe_not_in_yet': 'Рецепта в списке покупок нет.'
        })

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shpng_list = IngredientRecipe.objects.filter(
                recipe__shpngcart__user=request.user
            ).values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            ).order_by(
                'ingredient__name'
            ).annotate(
                amount=Sum('amount')
            ).values_list(
                'ingredient__name', 'amount', 'ingredient__measurement_unit'
            )
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'
            ] = ('attachment; filename="somefilename.pdf"')
        p = canvas.Canvas(response, pagesize=A4)
        left_position = 50
        top_position = 700
        p.drawString(left_position, top_position + 40, "Список покупок:")

        for number, item in enumerate(shpng_list, start=1):
            p.drawString(
                left_position,
                top_position,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f'{item["ingredient__measurement_unit"]}'
            )
            top_position = top_position - 40

        p.showPage()
        p.save()
        return response

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk):
        return self.fav_shpng_methods(request, pk, Favorite, {
            'recipe_alrdy_in': 'Рецепт уже добавлен в избранное',
            'recipe_not_in_yet': 'Рецепта еще нет в избранном'
        })


class TagViewSet(ModelViewSet):
    pagination_class = CustomPagination
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    filter_backends = (SearchFilter,
                       OrderingFilter)
    ordering = ('name',)
    pagination_class = CustomPagination
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
