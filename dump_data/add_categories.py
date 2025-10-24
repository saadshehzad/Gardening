import uuid

def add_categories(cursor=None):
    categories = [
        "Trees",
        "Flowers", 
        "Shrubs",
        "Herbs",
        "Grasses",
        "Fruits",
        "Vegetables",
        "Perennials",
        "Annuals",
        "Succulents"
    ]
    
    for category_name in categories:
        category_id = str(uuid.uuid4()).replace("-", "")
        desc = "Descr"
        image = "Img"

        try:
            cursor.execute("""
                INSERT INTO plant_category (id, name, description, image)
                VALUES (%s, %s, %s, %s);
            """, (category_id, category_name, desc, image))
             
        except Exception as e:
            print(f"Error creating {category_name}: {e}")