from django.core.management.base import BaseCommand
from django.db import connection
from plant.management.commands.add_categories import add_category
from plant.management.commands.add_plants import add_plant
from plant.management.commands.get_ids import get_category_ids
from plant.management.commands.get_ids import get_llm_ids
from plant.management.commands.add_llm import add_llm
import json
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()

        add_category(cursor)
        connection.commit()
        self.stdout.write(self.style.SUCCESS("All categories saved successfully"))

        add_llm(cursor)
        connection.commit()
        self.stdout.write(self.style.SUCCESS("All llms saved successfully"))

        get_category_ids(cursor)
        get_llm_ids(cursor)

        add_plant(cursor)
        connection.commit()
        self.stdout.write(self.style.SUCCESS("All plants saved successfully"))
    
    