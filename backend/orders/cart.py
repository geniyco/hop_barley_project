from decimal import Decimal
from django.conf import settings
from django.http import HttpRequest
from products.models import Product
from typing import Iterator, Any, Dict


class Cart:
    """
    Клас для керування кошиком покупця на основі Django Sessions.
    Реалізує бізнес-логіку додавання, видалення та валідації залишків на складі.
    """

    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Якщо кошика в сесії немає, ініціалізуємо порожній
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: Dict[str, Any] = cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> bool:
        """
        Додавання товару до кошика або оновлення його кількості.
        Повертає True, якщо додавання успішне, або False, якщо перевищено ліміт на складі.
        """
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart[product_id]['quantity'] + quantity

        # Перевірка наявності товару на складі згідно з ТЗ 3.3
        if new_quantity > product.stock:
            return False

        self.cart[product_id]['quantity'] = new_quantity
        self.save()
        return True

    def remove(self, product: Product) -> None:
        """Видалення товару з кошика."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Перебір елементів кошика та отримання об'єктів Product із бази даних.
        Оптимізує запити до БД.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_copy = self.cart.copy()
        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """Підрахунок загальної кількості товарів у кошику."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Підрахунок сумарної вартості всього кошика згідно з ТЗ 3.3."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self) -> None:
        """Очищення кошика в сесії."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self) -> None:
        """Повідомляємо Django, що сесію змінено і її треба зберегти."""
        self.session.modified = True