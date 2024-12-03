from datetime import datetime


def form_shopping_list(user, ingredients, recipe_names):
    format_time = datetime.now().strftime('%d-%m-%Y_%H_%M_%S')
    shopping_list = [
        f'Список покупок для {user.first_name} {user.last_name} '
        f'от {format_time}\n'
    ]
    for numbering, ingredient in enumerate(ingredients, start=1):
        shopping_list.append(
            f'{numbering}. {ingredient["ingredient__name"].capitalize()}'
        )
        shopping_list.append(
            ' - {amount} {ingredient__measurement_unit}\n'.format(**ingredient)
        )
    shopping_list.append(
        'Все эти продукты вам пригодятся для приготовления следующих рецептов:'
    )
    shopping_list.append('\n'.join(
        f'· {recipe_name}'
        for recipe_name in recipe_names
    ))
    shopping_list.append('\n\nС любовью, ваш Foodgram!')
    return ''.join(shopping_list)
