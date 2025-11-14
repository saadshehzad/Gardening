import uuid

def add_category(cursor):
    categories = [
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
    ]
    
    for category_name in categories:
        category_id = str(uuid.uuid4()).replace("-", "")
        description = "Description"
        image = "Img"

        try:
            cursor.execute("""
                INSERT INTO plant_category (id, name, description, image)
                VALUES (%s, %s, %s, %s);
            """, (category_id, category_name, description, image))
             
        except Exception as e:
            print(f"Error creating {category_name}: {e}")