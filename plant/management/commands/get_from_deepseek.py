import os
import json
import re
import time
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

class Command(BaseCommand):
    help = "Generate plant data from DeepSeek and save as JSON"

    def handle(self, *args, **options):
        load_dotenv()

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            self.stderr.write(self.style.ERROR("DEEPSEEK_API_KEY missing"))
            return

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        openai_client = OpenAI(api_key=os.getenv("OPENAI_CHATGPT_API_KEY"))

        plants = [
            # List of 160 plants
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

        chunk_size = 5
        chunks = [plants[i:i + chunk_size] for i in range(0, len(plants), chunk_size)]

        all_data = []

        def fix_json(text):
            if not text:
                return None
            # Fix quotes
            text = text.replace("’", "'").replace("“", '"').replace("”", '"')
            # Remove trailing commas
            text = re.sub(r",\s*}", "}", text)
            text = re.sub(r",\s*]", "]", text)
            # Remove newlines in strings
            text = re.sub(r'\n(?=[^"]*")', ' ', text)
            text = text.strip()
            try:
                return json.loads(text)
            except Exception:
                return None

        # Process each chunk with retries
        for idx, chunk in enumerate(chunks, start=1):
            chunk_text = ', '.join(f'"{p}"' for p in chunk)
            prompt = f"""
                You are an expert gardener (5+ years experience).  
                Generate structured plant data for a gardening app using the following fields:

                IMPORTANT: Return ONLY valid JSON. Do NOT include explanations, markdown, or extra text.
                Escape all quotes. Use straight quotes only. No trailing commas.
                Return JSON in this format:
                {{
                "data": [ ...objects... ]
                }}

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
                - Include llm="DeepSeek" for every plant.
                - give valid images, image format will be in a list.
                """
            success = False
            for attempt in range(3):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.4
                    )
                    text = response.choices[0].message.content.strip()
                    data = fix_json(text)
                    if not data or "data" not in data:
                        # Feed broken text to GPT to clean
                        repair_prompt = f"Repair this JSON into valid format without changing values:\n{text}"
                        repaired = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": repair_prompt}],
                            temperature=0
                        )
                        fixed_data = fix_json(repaired.choices[0].message.content)
                        if fixed_data and "data" in fixed_data:
                            all_data.extend(fixed_data["data"])
                    if data and "data" in data:
                        all_data.extend(data["data"])
                        success = True
                        break
                    else:
                        time.sleep(1)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Chunk {idx} attempt {attempt+1} error: {e}"))
                    time.sleep(1)
            if not success:
                self.stderr.write(self.style.ERROR(f"Chunk {idx} failed after 3 attempts"))

        # Save to JSON
        with open("plant_data_from_deepseek.json", "w") as f:
            json.dump(all_data, f, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Plant data generated successfully. Total plants: {len(all_data)}"
        ))
