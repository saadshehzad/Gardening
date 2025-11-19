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

    image_list = [
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
        "https://images.unsplash.com/photo-1501004318641-b39e6451bec6",
        "https://images.unsplash.com/photo-1562003389-9028ee36f1cf",
        "https://images.unsplash.com/photo-1501004318641-74c16f0c4460",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef",
        "https://images.unsplash.com/photo-1574226516831-e1dff420e12e",
        "https://images.unsplash.com/photo-1506801310323-534be5e7f1f5",
        "https://images.unsplash.com/photo-1501004318641-2cbd8d33f3de",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1501004318641-f078e8df36aa"
    ]

    for i, category_name in enumerate(categories):
        category_id = str(uuid.uuid4()).replace("-", "")
        description = "Description"
        image = image_list[i]

        try:
            cursor.execute("""
                INSERT INTO plant_category (id, name, description, image)
                VALUES (%s, %s, %s, %s);
            """, (category_id, category_name, description, image))

        except Exception as e:
            print(f"Error creating {category_name}: {e}")
