import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Класс загрузки базы данных тегов."""

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.IMPORTING_FILES_DIR, 'tags.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            models_list = [Tag(name=row[0], slug=row[1])
                           for row in csv.reader(file)]
            Tag.objects.bulk_create(models_list, ignore_conflicts=True)

        self.stdout.write(f'Successfully loaded data from {file_path}')
