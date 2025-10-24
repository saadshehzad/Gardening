import os
from dotenv import load_dotenv
from openai import OpenAI
import json


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def plant_data(chunk: str, model="gpt-4o-mini"):
    
    prompt = f"""
    You are an expert gardener (5+ years experience).  
    Generate structured plant data for a gardening app using the following model fields:

    FIELDS:
    id,name,category,description,image,
    variety_info,attributes,family,type,native,plant_dimension,
    growth_stage,days_to_maturity, mature_speed, mature_height,fruit_size,
    exposure,sunlight_requirement, soil_type, soil_ph, hardiness, temperature_min, temperature_max, humidity_preference,
    watering_interval,
    fertilizer_interval,
    trimming_interval,
    health_status,common_pests, disease_signs, treatment_methods,

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

    IMPORTANT:
    Always include every field listed above in your JSON output.
    Use realistic or placeholder values if uncertain, but never omit a field.
    Return ONLY the JSON array, no markdown formatting, no code blocks, no explanations.
    
    
    Text:
    {chunk}
    """


    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature = 0.7,
        max_tokens = 6000, 
    )

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        with open('plant_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        return data
    
    except Exception as e:
        print (f"error parsing GPT response : {e}")
        print ("GPT output:", response.choices[0].message.content.strip())
        return []

plant_data(chunk="")


if os.path.exists('plant_data.json'):
    print(f"✓ File created successfully at: {os.path.abspath('plant_data.json')}")
else:
    print("✗ File was not created")