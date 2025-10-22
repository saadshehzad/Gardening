# import pytest
# from django.urls import reverse
# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
# from .models import Lawn,UserLawn,LawnPlant,RealGardenImages
# from plant.models import Plant,Category
# from users.models import User
# import json


# # Create your tests here.

# #Fixtures:
# @pytest.fixture
# def api_client():
#     return APIClient()

# User = get_user_model()
# @pytest.fixture
# def authenticated_user():
#     return User.objects.create_user(
#         username='testuser',
#         password='password123')

# @pytest.fixture
# def authenticated_client(api_client,authenticated_user):
#     api_client.force_authenticate(user=authenticated_user)
#     return api_client

# @pytest.fixture
# def create_user_lawn(create_lawn,authenticated_user):
#     user_lawn = UserLawn.objects.create(
#         lawn = create_lawn,
#         user = authenticated_user,
#         location = "not provided"
#     )
#     return user_lawn

# @pytest.fixture
# def create_user():
#     user = User.objects.create(
#         phone = "03205647332",
#         country = "USA",
#         verified = True
#     )
#     return user

# @pytest.fixture
# def create_lawn():
#     lawn = Lawn.objects.create(
#         name = "MyLawn"
#     )
#     return lawn

# @pytest.fixture
# def create_category():
#     category = Category.objects.create(
#     name = 'cat2',
#     description = 'abc',
#     image = '1'
#     )
#     return category

# @pytest.fixture
# def create_plant(create_category):
#     return Plant.objects.create(
#         name = 'Plant 2',
#         description = 'xyz',
#         image = '{"image": "1111"}',
#         days_to_maturity = '2',
#         mature_speed = '2',
#         mature_height = '2',
#         fruit_size = '2',
#         family = '2',
#         type = '2',
#         native = '2',
#         hardiness = '2',
#         exposure = '2',
#         plant_dimension = '2',
#         variety_info = '2',
#         attributes = '2',
#         category = create_category,
#         planted_date = '2025-09-11',
#         fertilizer_interval = '2',
#         trimming_interval = '2',
#         notification_send_date_and_type = '{}',
#     )

# @pytest.fixture
# def create_lawn_plant(create_lawn,create_plant,authenticated_user):
#     lawn_plant = LawnPlant.objects.create(
#         lawn = create_lawn,
#         plant = create_plant,
#         user = authenticated_user
#     )
#     return lawn_plant

# @pytest.fixture
# def create_real_garden_image():
#     return RealGardenImages.objects.create(
#         description = "newimage", 
#         image = "image",
#     )


# #Tests:
# @pytest.mark.django_db
# def test_create_lawn(create_lawn,authenticated_client):
#     lawn = create_lawn

#     url = reverse("lawn-list-api")
#     response = authenticated_client.get(url)

#     json_response = json.loads(response.content)

#     assert json_response
#     assert json_response[0]['id']
#     assert json_response[0]['name'] == 'MyLawn'
    
# @pytest.mark.django_db
# def test_retrieve_user_lawn(create_user_lawn,authenticated_client):
#     lawn = create_user_lawn

#     url = reverse("user-lawn-retrieve")
#     response = authenticated_client.get(url)

#     json_response = json.loads(response.content)
#     data = json_response[0] if isinstance(json_response, list) else json_response
    

#     assert json_response
#     assert response.status_code == 200
#     assert data["lawn"]["name"] == "MyLawn"

# @pytest.mark.django_db
# def test_lawn_detail(create_lawn,authenticated_client):
#     #arrange:
#     lawn = create_lawn
    
#     #act:
#     url = reverse("lawn-detail",args=[str(lawn.id)])
#     response = authenticated_client.get(url)

#     #response:
#     json_response = json.loads(response.content)
#     data = json_response[0] if isinstance(json_response, list) else json_response

#     #assert:
#     assert response.status_code == 200
#     assert data
#     assert data["name"] == "MyLawn"

# @pytest.mark.django_db
# def test_user_lawn(create_user_lawn,create_lawn_plant,create_lawn,create_plant,authenticated_client):
#     user_lawn = create_user_lawn
#     lawn_plant = create_lawn_plant
#     lawn = create_lawn
#     plant = create_plant

#     url = reverse("user-lawn-API-view")
#     response = authenticated_client.get(url)

#     #response:
#     json_response = json.loads(response.content)
#     data = json_response[0] if isinstance(json_response, list) else json_response

#     assert json_response
#     assert response.status_code == 200, response.content
#     assert data
#     assert data["lawn"]
#     assert data["plant"]

# @pytest.mark.django_db
# def test_real_garden_image(create_real_garden_image,authenticated_client):
#     image = create_real_garden_image

#     url = reverse("garden-image")
#     response = authenticated_client.get(url)

#     json_response = json.loads(response.content)
#     data = json_response[0] if isinstance(json_response, list) else json_response

    
#     assert json_response
#     assert response.status_code == 200, response.content
#     assert data['image'] == 'image'
#     assert data['description'] == 'newimage'

# @pytest.mark.django_db
# def test_real_garden_image_detail(create_real_garden_image,authenticated_client):
#     #Arrange:
#     image = create_real_garden_image
    
#     #Act:
#     url = reverse("garden-image-detail", kwargs={"pk": image.id})
#     response = authenticated_client.get(url)

#     #Assert:
#     json_response = json.loads(response.content)
#     data = json_response[0] if isinstance(json_response, list) else json_response
#     #Assert:
#     assert json_response
#     assert response.status_code == 200, response.content
#     assert data['image'] == 'image'
#     assert data['description'] == 'newimage'


# import google.generativeai as genai

# genai.configure(api_key="AIzaSyCs7l4ptdhfXANpPpgwPDxGulTHOOGRUXc")


# model = genai.GenerativeModel("gemini-1.5-flash")

# response = model.generate_content("Write a haiku about Python programming.")

# print(response.text)



from google import genai

client = genai.Client(api_key="AIzaSyCs7l4ptdhfXANpPpgwPDxGulTHOOGRUXc")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)