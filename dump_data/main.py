from dataclasses import dataclass
import os
import psycopg2
from dotenv import load_dotenv
from add_categories import add_categories
from get_categories import get_category_ids
from add_plants import insert_plant
import json

load_dotenv()

@dataclass
class Run:
    def get_db_connection(self):
        self.connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return self.connection.cursor()

    def create_categories(self):
        add_categories(self.get_db_connection())
        self.connection.commit()
        print("All the categories has been saved successfully.")
    
    def get_all_categories(self):
        data = get_category_ids(cursor=self.get_db_connection())
        # print(data)

    def add_plants(self):
        with open('plant_data.json', 'r') as f:
            loaded_data = json.load(f)
        insert_plant(cursor=self.get_db_connection(),plants=loaded_data)
        self.connection.commit()
        print("All the plants has been saved successfully.")

    def run(self):
        # self.create_categories()
        self.get_all_categories()
        self.add_plants()




Run().run()