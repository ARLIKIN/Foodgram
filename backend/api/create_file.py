from django.db.models import F


def create_file_str(shopping_cart):
    ingredients = []
    for card in shopping_cart:
        ingredients.append(
            card.recipe.ingredients.values(
                'name', 'measurement_unit',
                amount=F('recipe_ingredients__amount')
            ).first()
        )
    unique_objects = {}
    file = ''
    for ingredient in ingredients:
        key = (ingredient['name'], ingredient['measurement_unit'])
        if key in unique_objects:
            unique_objects[key].append(ingredient)
        else:
            unique_objects[key] = [ingredient]
    for key, ingredient_list in unique_objects.items():
        total_amount = sum(obj['amount'] for obj in ingredient_list)
        file += f'{key[0]} ({key[1]}) — {total_amount}\n'
    return file
