from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название ингредиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Ед. измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Модель тегов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        db_index=True
    )
    color = ColorField(
        format='hex',
        verbose_name='HEX-код цвета'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """
    Моодель рецепт.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        blank=True,
        verbose_name='Фото рецепта',
        upload_to='recipes/images'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки, мин.'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """
    Модель ингредиентов в рецепте.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        default=1,
        verbose_name='Количество ингредиента'
    )

    class Meta:
        default_related_name = 'ingridients_recipe'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} – {self.amount}'
