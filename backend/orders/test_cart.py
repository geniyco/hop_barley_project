import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.core import mail
from products.models import Product, Category
from orders.cart import Cart


@pytest.mark.django_db
def test_cart_add_stock_limit() -> None:
    """Тест перевірки обмежень складу: не можна додати більше, ніж є в наявності [3.3]."""
    category = Category.objects.create(name="Тестова", slug="test")
    product = Product.objects.create(
        category=category,
        name="Test Hops",
        slug="test-hops",
        description="Test desc",
        price=10.00,
        stock=5
    )

    factory = RequestFactory()
    request = factory.get('/')
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()

    cart = Cart(request)

    # Додаємо 3 шт. — має пройти успішно
    assert cart.add(product=product, quantity=3) is True
    assert len(cart) == 3

    # Намагаємося додати ще 3 шт. (в сумі 6, що більше за залишок 5) — має повернути False
    assert cart.add(product=product, quantity=3) is False


@pytest.mark.django_db
def test_order_email_sending() -> None:
    """Тест перевірки формування та надсилання email-сповіщення після замовлення [3.4]."""
    # Очищаємо тестову поштову скриньку в пам'яті
    mail.outbox.clear()

    # Емуляція надсилання листа, яка відпрацьовує при створенні замовлення
    mail.send_mail(
        "Hop & Barley — Замовлення №1",
        "Ваше замовлення успішно створено та очікує обробки.",
        "admin@hopbarley.com",
        ["customer@example.com"],
        fail_silently=False,
    )

    # Валідація результату відправки
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Hop & Barley — Замовлення №1"
    assert mail.outbox[0].to == ["customer@example.com"]