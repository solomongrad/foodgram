import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from recipes.models import Ingredients

User = get_user_model()


class Command(BaseCommand):
    """Класс загрузки базы данных ингредиентов."""

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.IMPORTING_FILES_DIR, 'ingredients.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            models_list = [Ingredients(name=row[0], measurement_unit=row[1])
                           for row in csv.reader(file)]
            Ingredients.objects.bulk_create(models_list, ignore_conflicts=True)

        self.stdout.write(f'Successfully loaded data from {file_path}')
