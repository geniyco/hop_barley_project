from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Форма для збору контактних даних покупця та адреси доставки.
    Повністю валідує поля відповідно до Пункту 3.4 ТЗ.
    """
    PAYMENT_CHOICES = [
        ('card', 'Кредитна картка (Імітація)'),
        ('cash', 'Оплата при отриманні'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Спосіб оплати"
    )

    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'placeholder': 'Введіть вашу повну адресу доставки...',
                'rows': 3,
                'style': 'width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ccc;'
            }),
        }