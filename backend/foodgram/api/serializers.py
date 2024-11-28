from django.db import transaction
from rest_framework import serializers, status
from djoser.serializers import UserSerializer as DjoserUserSerializer

from core.serializers import Base64ImageField
from recipes.models import (
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Ingredients
)
from users.models import User, Subscribtion


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            user=user.id,
            author=obj.id
        ).exists()


class AvatarSerializer(serializers.Serializer):
    """Сериализер аватара."""

    avatar = Base64ImageField(required=False)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredients.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class BaseRecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipesReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient',
    )

    class Meta(BaseRecipesSerializer.Meta):
        fields = (
            *BaseRecipesSerializer.Meta.fields,
            'tags', 'ingredients', 'author', 'text',
            'is_favorited', 'is_in_shopping_cart'
        )
        model = Recipe

    def is_object_in_model(self, obj, model):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return model.objects.filter(author=request.user,
                                    recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.is_object_in_model(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.is_object_in_model(obj, ShoppingCart)


class RecipesChangeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
    )

    class Meta(BaseRecipesSerializer.Meta):
        fields = (*BaseRecipesSerializer.Meta.fields,
                  'tags', 'ingredients', 'author', 'text')
        model = Recipe
        read_only_fields = ('author', )

    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        tags = data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                'Требуется хотя бы 1 ингредиент!'
            )
        if not tags:
            raise serializers.ValidationError(
                'Требуется хотя бы 1 тег!'
            )
        ingredients_list = {
            ingredient['ingredient'].get('id') for ingredient in ingredients
        }
        tags_list = {
            ingredient.id for ingredient in tags
        }
        if len(ingredients_list) != len(ingredients):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые ингредиенты в один рецепт!'
            )
        if len(tags_list) != len(tags):
            raise serializers.ValidationError(
                'Нельзя добавлять несколько одинаковых тегов в один рецепт!'
            )
        return data


    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredients.objects.get(id=ingredient['ingredient'].get('id').id),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(ingredients=ingredients, recipe=recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(ingredients=ingredients,
                                        recipe=instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipesReadSerializer(instance, context=self.context).data


class SubscribtionSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        read_only_fields = fields

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    def get_recipes(self, obj):
        limit = 10
        recipes = obj.recipe.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = BaseRecipesSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribtion.objects.filter(user=user, author=obj)


class SubscriptionChangeSerializer(serializers.ModelSerializer):
    """Сериалайзер для фолловеров. Только на запись."""

    author = UserSerializer
    user = UserSerializer

    class Meta:
        model = Subscribtion
        fields = ('author', 'user')

    def validate(self, data):
        author_id = data['author']
        user_id = data['user']
        if Subscribtion.objects.filter(
            author=author_id, user=user_id
        ).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user_id == author_id:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return SubscribtionSerializer(instance.author, context={'request': self.context.get('request')}).data