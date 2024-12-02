def form_shopping_list(user, ingredients, recipe_names, format_time):
    shopping_list = (
        f'Список покупок для {user.first_name} {user.last_name} '
        f'от {format_time}\n'
    )
    for i in range(len(ingredients)):
        shopping_list += (
            f'{i+1}. {ingredients[i]["ingredient__name"].capitalize()}'
            f' - {ingredients[i]["amount"]} '
            f'{ingredients[i]["ingredient__measurement_unit"]}\n'
        )
    shopping_list += (
        'Все эти продукты вам пригодятся для приготовления следующих рецептов:'
    )
    shopping_list += ''.join(
        f'\n· {recipe_name}'
        for recipe_name in recipe_names
    )
    shopping_list += '\n\nС любовью, ваш Foodgram!'
    return shopping_list
