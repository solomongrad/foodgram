import json
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from recipes.models import Ingredients

User = get_user_model()


class Command(BaseCommand):
    """Класс загрузки базы данных ингредиентов."""

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.IMPORTING_FILES_DIR,
                                 'ingredients.json')
        with open(file_path, mode='r', encoding='utf-8') as file:
            models_list = [Ingredients(
                name=row['name'], measurement_unit=row['measurement_unit']
            )
                for row in json.load(file)]
            Ingredients.objects.bulk_create(models_list, ignore_conflicts=True)

        self.stdout.write(f'Successfully loaded data from {file_path}')