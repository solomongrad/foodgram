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
        file_path = os.path.join(settings.CSV_FILES_DIR, 'tags.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            models_list = []
            for row in reader:
                name, slug = row
                if Tag.objects.filter(name=name, slug=slug).exists():
                    continue
                models_list += (Tag(name=name, slug=slug),)
            Tag.objects.bulk_create(models_list)

        self.stdout.write(f'Successfully loaded data from {file_path}')
