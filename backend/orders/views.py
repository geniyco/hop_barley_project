from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.db import transaction  # Для використання транзакцій згідно з ТЗ 3.4
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from django.core.mail import send_mail

from products.models import Product
from .cart import Cart
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .serializers import OrderSerializer  # ІМПОРТ ВИПРАВЛЕНО ЗГІДНО З ТЗ [3.7]


# ==========================================
# 1. ВЕБ-ІНТЕРФЕЙС (Django Templates & Sessions)
# ==========================================

@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    """Обробник для додавання товару до кошика з валідацією залишків [3.3]."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    quantity_str = request.POST.get('quantity', '1')
    quantity = int(quantity_str) if quantity_str.isdigit() else 1

    override_quantity_str = request.POST.get('override', 'False')
    override_quantity = override_quantity_str == 'True'

    success = cart.add(product=product, quantity=quantity, override_quantity=override_quantity)

    if success:
        messages.success(request, f"Товар '{product.name}' успішно додано до кошика!")
    else:
        messages.error(request, f"Не вдалося додати товар. На складі залишилось лише {product.stock} шт.")

    return redirect('orders:cart_detail')


def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    """Обробник для видалення товару з кошика [3.3]."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"Товар '{product.name}' видалено з кошика.")
    return redirect('orders:cart_detail')


def cart_detail(request: HttpRequest) -> HttpResponse:
    """Відображення сторінки вмісту кошика (ТЗ 3.3)."""
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


def order_create(request: HttpRequest) -> HttpResponse:
    """
    Обробник для оформлення замовлення.
    Використовує транзакції (transaction.atomic) для безпечного збереження даних та надсилає email [3.4].
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Ваш кошик порожній. Оформлення замовлення неможливе.")
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)

                    if request.user.is_authenticated:
                        order.user = request.user
                    else:
                        User = get_user_model()
                        admin_user = User.objects.first()
                        if not admin_user:
                            raise ValueError("Спочатку потрібно створити хоча б одного користувача (адміна) в системі.")
                        order.user = admin_user

                    order.total_price = cart.get_total_price()
                    order.status = 'pending'
                    order.save()

                    for item in cart:
                        product = item['product']
                        quantity = item['quantity']

                        if product.stock < quantity:
                            raise ValueError(
                                f"Товару '{product.name}' недостатньо на складі (доступно: {product.stock} шт.).")

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=item['price']
                        )

                        product.stock -= quantity
                        product.save()

                    cart.clear()

                    # НАДСИЛАННЯ EMAIL-СПОВІЩЕННЯ ЗГІДНО З ТЗ 3.4
                    subject = f"Hop & Barley — Замовлення №{order.id}"
                    message = (
                        f"Вітаємо, {order.user.username}!\n\n"
                        f"Ваше замовлення №{order.id} успішно створено.\n"
                        f"Адреса доставки: {order.shipping_address}\n"
                        f"Загальна сума: ${order.total_price}\n\n"
                        f"Дякуємо за покупку в Hop & Barley!"
                    )
                    # Надсилаємо на email користувача (якщо є) або на дефолтну адресу
                    recipient = order.user.email if order.user.email else 'customer@example.com'
                    send_mail(
                        subject,
                        message,
                        'admin@hopbarley.com',
                        [recipient],
                        fail_silently=True,
                    )

                messages.success(request, f"Дякуємо! Ваше замовлення №{order.id} успішно створено.")
                return redirect('products:product_list')

            except ValueError as e:
                messages.error(request, str(e))
            except Exception:
                messages.error(request, "Виникла помилка під час обробки замовлення. Спробуйте пізніше.")
    else:
        form = OrderCreateForm()

    return render(request, 'checkout.html', {'cart': cart, 'form': form})
# ==========================================
# 2. REST API (Django REST Framework)
# ==========================================

class OrderViewSet(viewsets.ModelViewSet):
    """
    API ендпоінт для замовлений (/api/orders/) згідно з ТЗ 3.7.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def perform_create(self, serializer):
        cart = Cart(self.request)
        order = serializer.save(user=self.request.user, total_price=cart.get_total_price())

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            item['product'].stock -= item['quantity']
            item['product'].save()

        cart.clear()