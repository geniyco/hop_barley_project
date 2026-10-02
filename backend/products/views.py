from django.views.generic import ListView, DetailView
from django.db.models import QuerySet, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from typing import Any

from .models import Product, Category, Review
from .serializers import ProductSerializer, ReviewSerializer

class ProductListView(ListView):
    """
    Контролер для відображення каталогу товарів (головна сторінка магазину).
    Реалізує пагінацію, пошук та фільтрацію згідно з Пунктом 3.1 ТЗ.
    """
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 9  # Відображаємо по 9 товарів на сторінці згідно з ТЗ

    def get_queryset(self) -> QuerySet[Product]:
        # Базовий запит: лише активні товари. Оптимізуємо запит через select_related (захист від N+1)
        queryset: QuerySet[Product] = Product.objects.filter(is_active=True).select_related('category')

        # 1. Пошук за назвою та описом (параметр ?q=...)
        query: str = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # 2. Фільтрація за категорією (параметр ?category=slug)
        category_slug: str = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # 3. Фільтрація за діапазоном цін (min_price та max_price)
        min_price: str = self.request.GET.get('min_price', '')
        max_price: str = self.request.GET.get('max_price', '')
        if min_price.isdigit():
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price.isdigit():
            queryset = queryset.filter(price__lte=float(max_price))

        # 4. Сортування за ціною, популярністю та новизною
        sort_by: str = self.request.GET.get('sort', '')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-stock')  # Імітація популярності за залишками на складі
        else:
            queryset = queryset.order_by('-created_at')  # Новинки за замовчуванням

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Передаємо кореневі категорії для побудови бічного меню фільтрації
        context['categories'] = Category.objects.filter(parent=None).prefetch_related('children')
        return context

class ProductDetailView(DetailView):
    """
    Контролер для відображення детальної сторінки товару.
    Знаходить товар за його унікальним <slug> згідно з ТЗ.
    """
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'  # Вказуємо, що пошук у БД йде по полю slug із ТЗ

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Оптимізовано завантажуємо відгуки до цього товару разом з авторами (select_related)
        context['reviews'] = self.object.reviews.select_related('user')
        return context


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ендпоінт для перегляду товарів.
    Реалізує список (з пагінацією) та деталі товару згідно з ТЗ 3.7.
    Підтримує пошук та сортування.
    """
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Налаштування фільтрації та пошуку з ТЗ
    filterset_fields = ['category__slug']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']


class ReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API ендпоінт для відгуків товарів за адресою /api/products/<id>/reviews/.
    Дозволяє переглядати (GET) та додавати відгук (POST) згідно з ТЗ 3.7.
    """
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']).select_related('user')

    def perform_create(self, serializer):
        # Автоматично прив'язуємо поточного користувача API та товар
        product = Product.objects.get(id=self.kwargs['product_pk'])
        serializer.save(user=self.request.user, product=product)