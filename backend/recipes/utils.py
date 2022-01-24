from backend.recipes.models import Recipe, RecipeIngredient


def create_update_recipe(validated_data, instance=None):
    ingredients = validated_data.pop('ingredients', None)
    tags = validated_data.pop('tags', None)
    if instance is None:
        instance = Recipe.objects.create(**validated_data)
    if tags is not None:
        instance.tags.set(tags)
    if ingredients is not None:
        instance.ingredients.clear()
        create_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)
    return instance
