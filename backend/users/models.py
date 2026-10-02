from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомна модель користувача.
    Розширює стандартну модель Django додатковими полями для магазину.
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )
    shipping_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Адреса доставки"
    )

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self) -> str:
        return self.username
