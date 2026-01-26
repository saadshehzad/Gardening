# Run inside: python manage.py shell

from django.db import transaction
from django.apps import apps
from django.db.models import F
from django.db.models.functions import Lower

# CHANGE these if your app/model names differ
Plant = apps.get_model("plant", "Plant")   # <-- your app label + model
Season = apps.get_model("plant", "Season") # <-- your app label + model

plant_season = {
    "Apple": "fall",
    "Crabapple": "fall",
    "Pear": "fall",
    "Peach": "summer",
    "Plum": "summer",
    "Apricot": "summer",
    "Cherry": "summer",
    "Blueberry": "summer",
    "Cranberry": "fall",
    "Blackberry": "summer",
    "Raspberry": "summer",
    "Strawberry": "summer",
    "Grape": "fall",
    "Watermelon": "summer",
    "Cantaloupe": "summer",
    "Avocado": "winter",
    "Orange": "winter",
    "Lemon": "winter",
    "Lime": "winter",
    "Papaya": "summer",
    "Pineapple": "summer",
    "American Persimmon": "fall",
    "Pawpaw": "fall",
    "Elderberry": "summer",
    "Mulberry": "summer",
    "Gooseberry": "summer",
    "Basil": "summer",
    "Mint": "summer",
    "Oregano": "summer",
    "Thyme": "summer",
    "Rosemary": "summer",
    "Sage": "summer",
    "Cilantro": "spring",
    "Parsley": "spring",
    "Dill": "spring",
    "Chives": "spring",
    "Tarragon": "spring",
    "Marjoram": "summer",
    "Catnip": "summer",
    "Wild Bergamot": "summer",
    "Yarrow": "summer",
    "Sunflower": "summer",
    "Black-Eyed Susan": "summer",
    "Coneflower": "summer",
    "Goldenrod": "fall",
    "Aster": "fall",
    "Columbine": "spring",
    "Lupine": "spring",
    "Milkweed": "summer",
    "Marigold": "summer",
    "Daisy": "spring",
    "Wild Rose": "summer",
    "Fireweed": "summer",
    "Bluebell": "spring",
    "Trillium": "spring",
    "Violet": "spring",
    "Iris": "spring",
    "Phlox": "summer",
    "Lavender": "summer",
    "Petunia": "summer",
    "Impatiens": "summer",
    "Zinnia": "summer",
    "Snapdragon": "spring",
    "Daylily": "summer",
    "Hosta": "summer",
    "Peony": "spring",
    "White Oak": "spring",
    "Red Oak": "spring",
    "Sugar Maple": "spring",
    "Red Maple": "spring",
    "Sycamore": "spring",
    "Birch": "spring",
    "Aspen": "spring",
    "Cottonwood": "spring",
    "Hickory": "spring",
    "Black Walnut": "fall",
    "Cherry Tree": "spring",
    "Apple Tree": "spring",
    "Magnolia": "spring",
    "Dogwood": "spring",
    "Redwood": "spring",
    "Sequoia": "spring",
    "Cedar": "spring",
    "Hemlock": "spring",
    "Juniper": "spring",
    "Ponderosa Pine": "spring",
    "White Pine": "spring",
    "Lodgepole Pine": "spring",
    "Sitka Spruce": "spring",
    "White Spruce": "spring",
    "Douglas Fir": "spring",
    "Balsam Fir": "spring",
    "Rhododendron": "spring",
    "Azalea": "spring",
    "Mountain Laurel": "spring",
    "Elderberry Shrub": "summer",
    "Blueberry Shrub": "summer",
    "Manzanita": "spring",
    "Sagebrush": "summer",
    "Sumac": "fall",
    "Gooseberry Shrub": "summer",
    "Snowberry": "fall",
    "Agave": "summer",
    "Aloe": "summer",
    "Prickly Pear Cactus": "summer",
    "Saguaro Cactus": "summer",
    "Barrel Cactus": "summer",
    "Yucca": "summer",
    "Sedum": "summer",
    "Echeveria": "summer",
    "Century Plant": "summer",
    "Buffalo Grass": "summer",
    "Blue Grama": "summer",
    "Big Bluestem": "summer",
    "Little Bluestem": "summer",
    "Switchgrass": "summer",
    "Wild Rye": "spring",
    "Wheat": "spring",
    "Barley": "spring",
    "Oats": "spring",
    "Chanterelle": "summer",
    "Oyster Mushroom": "fall",
    "Hen-of-the-Woods": "fall",
    "Porcini": "summer",
    "Lion's Mane": "fall",
    "Corn": "summer",
    "Tomato": "summer",
    "Potato": "spring",
    "Bell Pepper": "summer",
    "Chili Pepper": "summer",
    "Pumpkin": "fall",
    "Butternut Squash": "fall",
    "Acorn Squash": "fall",
    "Zucchini": "summer",
    "Lettuce": "spring",
    "Spinach": "spring",
    "Kale": "spring",
    "Broccoli": "spring",
    "Cauliflower": "spring",
    "Carrot": "spring",
    "Onion": "spring",
    "Garlic": "fall",
    "Sweet Potato": "summer",
    "Cucumber": "summer",
    "Green Beans": "summer",
    "Okra": "summer",
    "Turnip": "fall",
    "Cabbage": "spring",
}


def run():
    # seasons (create once)
    season_obj = {s: Season.objects.get_or_create(name=s)[0] for s in ("winter", "spring", "summer", "fall")}

    # build case-insensitive lookup: lower(name_in_db) -> Plant
    plants_by_lower = {
        p.name.lower(): p
        for p in Plant.objects.all().only("id", "name")
        if p.name
    }

    # 1) clear seasons for ALL plants
    for p in Plant.objects.all().only("id"):
        p.seasons.clear()

    # 2) assign exactly one season per plant (case-insensitive)
    updated = 0
    missing = []

    for raw_name, s in plant_season.items():
        key = (raw_name or "").strip().lower()
        plant = plants_by_lower.get(key)
        if not plant:
            missing.append(raw_name)
            continue
        plant.seasons.set([season_obj[s]])  # ensures exactly 1
        updated += 1

    print("Updated:", updated)
    print("Missing:", len(missing))
    for m in missing[:50]:
        print("-", m)

run()