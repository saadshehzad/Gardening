from plant.management.commands.get_ids import get_category_ids,get_llm_ids
import uuid
import json
import os

def add_plant(cursor):
    data_from_llms = {
        "ChatGPT": os.path.join(os.getcwd(), "plant_data_from_gpt.json"),
        "DeepSeek": os.path.join(os.getcwd(), "plant_data_from_deepseek.json")
    }

    category_ids = get_category_ids(cursor)
    llm_ids = get_llm_ids(cursor)
    

    for llm_name,json_path in data_from_llms.items():
        with open(json_path, "r") as f:
            loaded_data = json.load(f)

        for plant in loaded_data:
            plant_name = plant.get("name")
            category_name = plant.get("category")
            category_id = category_ids.get(category_name)
            llm_id = llm_ids.get(llm_name)
            try:
                cursor.execute("""
                    INSERT INTO plant_plant (
                        id, name, category_id, llm_id, description, image, variety_info, attributes,
                        family, type, native, plant_dimension, growth_stage, days_to_maturity,
                        mature_speed, mature_height, fruit_size, exposure, sunlight_requirement,
                        soil_type, soil_ph, hardiness, temperature_min, temperature_max,
                        humidity_preference, watering_interval, last_watered, next_watering_date,
                        fertilizer_interval, last_fertilized, next_fertilizing_date, trimming_interval,
                        last_trimmed, next_trimming_date, planted_date, health_status, common_pests,
                        disease_signs, treatment_methods, notification_send_date_and_type
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    plant_name,
                    category_id,
                    llm_id,
                    plant.get("description", ""),
                    json.dumps(plant.get("image", {})),
                    plant.get("variety_info", ""),
                    plant.get("attributes", ""),
                    plant.get("family", ""),
                    plant.get("type", ""),
                    plant.get("native", ""),
                    plant.get("plant_dimension", ""),
                    plant.get("growth_stage", "Seed"),
                    plant.get("days_to_maturity", ""),
                    plant.get("mature_speed", ""),
                    plant.get("mature_height", ""),
                    plant.get("fruit_size", ""),
                    plant.get("exposure", ""),
                    plant.get("sunlight_requirement", ""),
                    plant.get("soil_type", ""),
                    plant.get("soil_ph", ""),
                    plant.get("hardiness", ""),
                    plant.get("temperature_min", ""),
                    plant.get("temperature_max", ""),
                    plant.get("humidity_preference", ""),
                    plant.get("watering_interval", 7),
                    None,
                    None,
                    plant.get("fertilizer_interval", 14),
                    None,
                    None,
                    plant.get("trimming_interval", 30),
                    None,
                    None,
                    None,
                    None,
                    plant.get("common_pests", ""),
                    plant.get("disease_signs", ""),
                    plant.get("treatment_methods", ""),
                    None
                    ))   

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error inserting {plant.get('name')}: {e}")
                cursor.connection.rollback()
