from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    """
    Модель замовлення згідно з ТЗ.
    Зберігає інформацію про статус, загальну суму та адресу доставки.
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує оплати'),
        ('paid', 'Оплачено'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Користувач"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Загальна вартість"
    )
    shipping_address = models.TextField(verbose_name="Адреса доставки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Замовлення №{self.id} ({self.user.username})"


class OrderItem(models.Model):
    """
    Елемент замовлення згідно з ТЗ.
    Зберігає знімок ціни товару на момент покупки та кількість.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name="Товар"
    )
    quantity = models.IntegerField(default=1, verbose_name="Кількість")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна на момент покупки"
    )

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"