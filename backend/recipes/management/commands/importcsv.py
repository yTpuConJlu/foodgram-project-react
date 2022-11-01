import csv
import os
from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """Запуск импорта.

    python manage.py importcsv
    """

    def handle(self, *args, **kwargs):
        file = 'ingredients.csv'
        base_parent_dir = os.path.abspath(
            os.path.join(settings.BASE_DIR, os.pardir))
        with open(f'{base_parent_dir}app/data/{file}',
                  'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
        print('Ингредиенты импортированы.')
