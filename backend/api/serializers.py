from django.db.transaction import atomic
from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField,
                                        ValidationError)
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)

from users.models import Follow, User


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError(
                 {'errors': self.context['errors']['recipe_alrdy_in']})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(instance.recipe, context=context).data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit')


class IngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True)
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,)
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_recipe',)
    image = Base64ImageField()
    author = UsersSerializer(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()


class CreateIngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',)

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount'))


class RecipeShortInfo(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowListSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortInfo(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortInfo(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()

class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if self.context['request'].user.id == data['author']:
            raise ValidationError({
                'errors': 'Вы не можете подписаться на себя.'
            })
        if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Уже подписался.'
            })
        return data

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class CreateRecipeSerializer(ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time',)

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients])

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    @staticmethod
    def check_repit(data, errors):
        if not data:
            raise ValidationError(
                    {'errors': errors['is_empty']})
        check_list = []
        for item_to_chk in data:
            if item_to_chk in check_list:
                raise ValidationError(
                    {'errors': errors['is_repeat']})
            check_list.append(item_to_chk)
        return data

    def validate_ingredients(self, data):
        self.check_repit(
            data,
            {'is_repeat': 'Ингредиенты не должны повторяться в рецепте.',
             'is_empty': 'Должен быть хотя бы 1 ингредиент.'})
        return data

    def validate_tags(self, data):
        self.check_repit(
            data,
            {'is_repeat': 'Тэги не должны повторяться в рецепте.',
             'is_empty': 'Теги не должны быть пустыми'})
        return data

    def validate_cooking_time(self, data):
        if data < 1:
            raise ValidationError(
                'Готовить надо не менее 1 мин.')
        if data > 500:
            raise ValidationError(
                'Время приготовления не может быть более 500 мин.')
        return data

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        recipe = instance
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        self.create_tags(tags_data, instance)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request'), }).data


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'recipe',
            'user'
        )

    def validate(self, data):
        print(self.context['errors'])
        user = self.context['request'].user
        recipe_pk = data['recipe'].pk
        if ShoppingCart.objects.filter(user=user,
                                       recipe__pk=recipe_pk).exists():
            raise ValidationError(
                 {'errors': self.context['errors']['recipe_alrdy_in']})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(instance.recipe, context=context).data
