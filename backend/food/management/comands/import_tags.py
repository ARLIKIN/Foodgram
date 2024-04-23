import csv

from django.core.management.base import BaseCommand

from food.models import Tag


class Command(BaseCommand):
    help = 'Import data from CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('data/recipes_tag.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                Tag.objects.create(**row)
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
