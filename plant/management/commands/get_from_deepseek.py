import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_dotenv()

        api_key = os.getenv("DEEPSEEK_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

        chunk = ""
        prompt = f"""
        You are an expert gardener (5+ years experience).  
        Generate structured plant data for a gardening app using the following model fields:

        FIELDS:
        id,
        name,
        category,
        llm,(I have an extra field "llm", put "DeepSeek" in that field)
        description,
        image, (image format will be in list)
        variety_info,
        attributes,
        family,
        type,
        native,
        plant_dimension,
        growth_stage,
        days_to_maturity,
        mature_speed,
        mature_height,
        fruit_size,
        exposure,
        sunlight_requirement,
        soil_type,
        soil_ph,
        hardiness,
        temperature_min,
        temperature_max,
        humidity_preference,
        watering_interval,
        fertilizer_interval,
        trimming_interval,
        common_pests,
        disease_signs,
        treatment_methods,

        PLANTS:
        1. Sugar Maple (Acer saccharum)
        2. Douglas Fir (Pseudotsuga menziesii)
        3. White Oak (Quercus alba)
        4. Black-eyed Susan (Rudbeckia hirta)
        5. Purple Coneflower (Echinacea purpurea)
        6. Goldenrod (Solidago canadensis)
        7. Columbine (Aquilegia canadensis)
        8. American Beautyberry (Callicarpa americana)
        9. Mountain Laurel (Kalmia latifolia)
        10. Prairie Blazing Star (Liatris pycnostachya)

        REQUIREMENTS:
        - Fill all relevant fields with realistic, concise data.  
        - Keep numeric values consistent (e.g., temperature_min < temperature_max).  
        - Use natural, factual descriptions.  
        - Dates can be placeholders.  
        - Output only a valid JSON list where each plant is an object using the field names as keys.
        - keep data in key value pairs. 
        - keep all data in same format.

        IMPORTANT:
        Always include every field listed above in your JSON output.
        Use realistic or placeholder values if uncertain, but never omit a field.
        Return ONLY the JSON array, no markdown formatting, no code blocks, no explanations.

        And give the category name exact from these categories only, don't use s or es.
            "Tree",
            "Flower", 
            "Shrub",
            "Herb",
            "Grass",
            "Fruit",
            "Vegetable",
            "Perennial",
            "Annual",
            "Succulent"

        
        
        Text:
        {chunk}
        """

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=6000,
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"API Error: {e}"))
            return

        try:
            data = json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error parsing DeepSeek response: {e}"))
            self.stderr.write("DeepSeek OUTPUT:")
            self.stderr.write(response.choices[0].message.content.strip())
            return
        
        with open("plant_data_from_deepseek.json", "w") as f:
            json.dump(data, f, indent=2)

        self.stdout.write(self.style.SUCCESS("Plant data generated successfully."))
    

