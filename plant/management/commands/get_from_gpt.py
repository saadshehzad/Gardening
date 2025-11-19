import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import load_dotenv
from openai import OpenAI
import re


class Command(BaseCommand):

    def handle(self, *args, **options):
        load_dotenv()

        api_key = os.getenv("OPENAI_CHATGPT_API_KEY")
        if not api_key:
            self.stderr.write(self.style.ERROR("OPENAI_CHATGPT_API_KEY not found"))
            return

        client = OpenAI(api_key=api_key)

        plants = [
            "Corn", "Tomato", "Potato", "Bell Pepper", "Chili Pepper", "Pumpkin", "Butternut Squash",
            "Acorn Squash", "Zucchini", "Lettuce", "Spinach", "Kale", "Broccoli", "Cauliflower",
            "Carrot", "Onion", "Garlic", "Sweet Potato", "Cucumber", "Green Beans", "Peas", "Radish",
            "Beetroot", "Eggplant", "Celery", "Okra", "Turnip", "Cabbage", "Apple", "Crabapple", "Pear",
            "Peach", "Plum", "Apricot", "Cherry", "Blueberry", "Cranberry", "Blackberry", "Raspberry",
            "Strawberry", "Grape", "Watermelon", "Cantaloupe", "Avocado", "Orange", "Lemon", "Lime",
            "Papaya", "Pineapple", "American Persimmon", "Pawpaw", "Elderberry", "Mulberry", "Gooseberry",
            "Basil", "Mint", "Oregano", "Thyme", "Rosemary", "Sage", "Cilantro", "Parsley", "Dill",
            "Chives", "Tarragon", "Marjoram", "Catnip", "Wild Bergamot", "Yarrow", "Sunflower",
            "Black-Eyed Susan", "Coneflower", "Goldenrod", "Aster", "Columbine", "Lupine", "Milkweed",
            "Marigold", "Daisy", "Wild Rose", "Fireweed", "Bluebell", "Trillium", "Violet", "Iris",
            "White Oak", "Red Oak", "Sugar Maple", "Red Maple", "Ponderosa Pine", "White Pine",
            "Lodgepole Pine", "Sitka Spruce", "White Spruce", "Douglas Fir", "Balsam Fir", "Sycamore",
            "Birch", "Aspen", "Cottonwood", "Redwood", "Sequoia", "Cedar", "Hemlock", "Hickory",
            "Black Walnut", "Cherry Tree", "Apple Tree", "Magnolia", "Dogwood", "Juniper",
            "Rhododendron", "Azalea", "Mountain Laurel", "Elderberry Shrub", "Blueberry Shrub",
            "Manzanita", "Sagebrush", "Sumac", "Gooseberry Shrub", "Snowberry", "Agave", "Aloe",
            "Prickly Pear Cactus", "Saguaro Cactus", "Barrel Cactus", "Yucca", "Sedum", "Echeveria",
            "Century Plant", "Buffalo Grass", "Blue Grama", "Big Bluestem", "Little Bluestem",
            "Switchgrass", "Wheat", "Barley", "Oats", "Wild Rye", "Morel", "Chanterelle", "Oyster Mushroom",
            "Hen-of-the-Woods", "Porcini", "Lion’s Mane", "Daylily", "Hosta", "Peony", "Coneflower",
            "Black-Eyed Susan", "Phlox", "Lavender", "Marigold", "Petunia", "Impatiens", "Zinnia",
            "Snapdragon"
        ]

    
        chunk_size = 10
        chunks = [plants[i:i + chunk_size] for i in range(0, len(plants), chunk_size)]


        prompts = []
        for chunk in chunks:
            chunk_text = ', '.join(f'"{p}"' for p in chunk)
            prompt = f"""
            You are an expert gardener (5+ years experience).  
            Generate structured plant data for a gardening app using the following fields:
            
            IMPORTANT: Return ONLY valid JSON. Do NOT include explanations, markdown, or extra text.
            Escape all quotes. Use straight quotes only. No trailing commas.

            FIELDS:
            name, category, llm, description, image, variety_info, attributes, family, type, native,
            plant_dimension, growth_stage, days_to_maturity, mature_speed, mature_height, fruit_size,
            exposure, sunlight_requirement, soil_type, soil_ph, hardiness, temperature_min, temperature_max,
            humidity_preference, watering_interval, fertilizer_interval, trimming_interval, common_pests,
            disease_signs, treatment_methods

            PLANTS:
            [{chunk_text}]

            REQUIREMENTS:
            - Fill all fields with realistic or placeholder data.  
            - Use exact categories: "Tree", "Flower", "Shrub", "Herb", "Grass", "Fruit", "Vegetable",
            "Perennial", "Annual", "Succulent"
            - Output ONLY valid JSON, array of objects, key-value pairs.
            - Include llm="Chatgpt" for every plant.
            - give valid images, image format will be in a list.
            """
            prompts.append(prompt)

        all_plants_data = []

        for prompt in prompts:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                content = response.choices[0].message.content.strip()
                content = content.replace("```json", "").replace("```", "")
                content = content.replace("’", "'").replace("“", '"').replace("”", '"')
                content = re.sub(r",\s*}", "}", content)
                content = re.sub(r",\s*]", "]", content)
                chunk_data = json.loads(content)
                all_plants_data.extend(chunk_data)

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing chunk: {e}"))
                self.stderr.write("GPT OUTPUT:")
                self.stderr.write(content)
                continue

    
        with open("plant_data_from_gpt.json", "w") as f:
            json.dump(all_plants_data, f, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Plant data generated successfully. Total plants: {len(all_plants_data)}"
        ))

       