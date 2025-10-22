import pytest
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Plant,Category
from users.models import User
import json


#Fixtures:
#1) Authentication:
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_user():
    return User.objects.create_user(
        username='testuser',
        password='password123')

User = get_user_model()
@pytest.fixture
def authenticated_client(api_client,authenticated_user):
    api_client.force_authenticate(user=authenticated_user)
    return api_client

#2) feeding data:
@pytest.fixture
def create_category():
    category = Category.objects.create(
    name = 'cat2',
    description = 'abc',
    image = '1'
    )
    return category

@pytest.fixture
def create_plant(create_category):
    return Plant.objects.create(
        name = 'Plant 2',
        description = 'xyz',
        image = '{"image": "1111"}',
        days_to_maturity = '2',
        mature_speed = '2',
        mature_height = '2',
        fruit_size = '2',
        family = '2',
        type = '2',
        native = '2',
        hardiness = '2',
        exposure = '2',
        plant_dimension = '2',
        variety_info = '2',
        attributes = '2',
        category = create_category,
        planted_date = '2025-09-11',
        fertilizer_interval = '2',
        trimming_interval = '2',
        notification_send_date_and_type = '{}',
    )



# Tests:
# CategoryCreateAPIView
@pytest.mark.django_db
# class TestCategoryCreateAPI:
def test_create_category(create_category,authenticated_client):
    category = create_category

    url = reverse("category-list")
    response = authenticated_client.get(url)

    actual_data = json.loads(response.content)
    expected_data = [{"id": str(category.id), "name": "cat2", "description": "abc", "image": "1"}]

    assert actual_data == expected_data
    assert response.status_code == 200


#CategoryDetailAPIView
@pytest.mark.django_db
# class TestCategoryCreateAPI:
def test_retrieve_category(create_category,authenticated_client):
    category = create_category

    url = reverse("category-detail", args=[str(category.id)])
    response = authenticated_client.get(url)

    assert response.json()['name'] == create_category.name 
    assert response.status_code == 200



# PlantDetailAPIView
@pytest.mark.django_db
def test_retrieve_product(create_plant, authenticated_client):
    #arrange
    plant = create_plant
    # act
    url = reverse("product-detail",args=[str(plant.id)])
    response = authenticated_client.get(url)
    # assert
    assert response.status_code == 200
    assert response.json()["name"] == create_plant.name

#plantcreateAPIview
@pytest.mark.django_db
def test_create_product(create_plant,create_category, authenticated_client):
    #arrange
    plant = create_plant
    # act
    url = reverse("product-list")
    response = authenticated_client.get(url)
    # assert
    print(response.content)
    actual_data = json.loads(response.content)
    expected_result = [{
        'id':str(plant.id),
        'name' : 'Plant 2',
        'description' : 'xyz',
        'image' : '{"image": "1111"}',
        'days_to_maturity' : '2',
        'mature_speed' : '2',
        'mature_height' : '2',
        'fruit_size' : '2',
        'family' : '2',
        'type' : '2',
        'native' : '2',
        'hardiness' : '2',
        'exposure' : '2',
        'plant_dimension' : '2',
        'variety_info' : '2',
        'attributes' : '2',
        'category' : create_category,
        'planted_date' : '2025-09-11',
        'fertilizer_interval' : '2',
        'trimming_interval' : '2',
        'notification_send_date_and_type' : '{}',
    }]
    print(actual_data)
    print(expected_result)
    assert response.status_code == 200
    assert response
    assert expected_result
    assert actual_data