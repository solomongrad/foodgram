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
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                Ingredients.objects.update_or_create(
                    name=name, measurement_unit=measurement_unit
                )

        self.stdout.write(f'Successfully loaded data from {file_path}')
