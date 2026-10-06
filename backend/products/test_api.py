import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from products.models import Product, Category


@pytest.mark.django_db
def test_get_products_api():
    """Тест перевірки REST API каталогу товарів (ТЗ 3.7)."""
    category = Category.objects.create(name="Пиво", slug="beer")
    Product.objects.create(
        category=category, name="Citra", slug="citra", description="Desc", price=5.00, stock=10
    )

    client = APIClient()
    response = client.get('/api/products/')

    assert response.status_code == 200
    # Перевіряємо, що API повернуло список із нашим товаром
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Citra"


@pytest.mark.django_db
def test_api_user_registration():
    """Тест перевірки реєстрації користувача через REST API (ТЗ 3.7)."""
    client = APIClient()
    data = {
        "username": "api_buyer",
        "password": "SecurePassword123!",
        "email": "buyer@example.com"
    }
    # Зверніть увагу на префікс /users/, який ми налаштували в urls.py
    response = client.post('/users/api/users/register/', data, format='json')

    assert response.status_code == 201
    assert get_user_model().objects.filter(username="api_buyer").exists()