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
        file_path = os.path.join(settings.CSV_FILES_DIR, 'ingredients.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            models_list = []
            for row in reader:
                name, measurement_unit = row
                if Ingredients.objects.filter(
                    name=name, measurement_unit=measurement_unit
                ).exists():
                    continue
                models_list += (Ingredients(
                    name=name, measurement_unit=measurement_unit
                ),)
            Ingredients.objects.bulk_create(models_list)

        self.stdout.write(f'Successfully loaded data from {file_path}')
