from geopy import distance

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from star_burger.settings import YANDEX_API_KEY

from .helpers import fetch_coordinates


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True
    )
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name="ресторан"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт'
    )

    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):
    def total(self):
        subtotal = models.ExpressionWrapper(
            models.F('product_position__current_price')
            * models.F('product_position__quantity'),
            output_field=models.DecimalField()
        )

        return self.annotate(
            total=models.Sum(subtotal)
        )

    def fetch_restaurant_distance(self):
        restaurants = Restaurant.objects.all()

        known_points = {
            address: (lon, lat) for address, lon, lat in
            MapPoint.objects.values_list('address', 'lon', 'lat')
        }

        restaurant_points = {
            restaurant.id: known_points[restaurant.address]
            if restaurant.address in known_points.keys()
            else MapPoint.objects.save_point(restaurant.address)
            for restaurant in restaurants
        }

        menu_items = RestaurantMenuItem.objects \
            .filter(availability=True) \
            .order_by('product') \
            .values_list('product', 'restaurant')

        product_restaurants = {
            product: set() for product, restaurant in menu_items
        }

        for product, restaurant in menu_items:
            product_restaurants[product].add(restaurant)

        for order in self:
            suitable_restaurants_ids = set.intersection(
                *[product_restaurants[product.id] for product in order.products.all()]
            )

            order_point = known_points[order.address] if order.address in known_points.keys() \
                else MapPoint.objects.save_point(order.address)

            distances = [
                {
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'distance': distance.distance(
                        order_point, restaurant_points[restaurant.id]
                    ).km,
                } for restaurant in restaurants
                if restaurant.id in suitable_restaurants_ids
            ]

            order.distances = sorted(
                distances,
                key=lambda distance: distance['distance'],
            )

        return self


class Order(models.Model):
    STATUSES = [
        ('N', 'Новый'),
        ('P', 'В работе'),
        ('C', 'Выполнен')
    ]
    PAYMENT_METHOD = [
        ('C', 'Наличными при доставке'),
        ('O', 'Картой онлайн')
    ]
    firstname = models.CharField('Имя', max_length=200)
    lastname = models.CharField('Фамилия', max_length=200)
    phonenumber = PhoneNumberField('Телефон')
    address = models.TextField('Адрес')
    products = models.ManyToManyField(
        Product,
        through='OrderPosition',
        related_name='orders',
        verbose_name='Продукты')
    status = models.CharField(
        'Статус',
        max_length=2,
        choices=STATUSES,
        default='N'
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=2,
        choices=PAYMENT_METHOD,
        default='C'
    )
    comment = models.TextField('Комментарий', blank=True)
    created_time = models.DateTimeField('Заказ создан', default=timezone.now)
    called_time = models.DateTimeField('Время звонка', null=True, blank=True)
    delivered_time = models.DateTimeField(
        'Время доставки', null=True, blank=True)
    restaurants = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Ресторан',
        default=None,
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta():
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Заказ',
        related_name='product_position'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Товар',
        related_name='order_possition'
    )

    current_price = models.DecimalField(
        'Цена на момент заказа',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )

    quantity = models.IntegerField('Количество', default=1)

    def get_price(self):
        return self.product.price

    def __str__(self):
        return f'{self.product}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Заказанные товары'


class MapPointQuerySet(models.QuerySet):
    def save_point(self, address):
        current_address = self \
            .get_or_create(
                address=address,
                defaults={
                    'last_update': timezone.now,
                    **fetch_coordinates(
                        YANDEX_API_KEY, address
                    )
                }
            )

        return current_address.lon, current_address.lat


class MapPoint(models.Model):
    address = models.CharField('Адрес', max_length=300)
    lon = models.FloatField('Долгота')
    lat = models.FloatField('Широта')
    last_update = models.DateTimeField('Время обновления')

    objects = MapPointQuerySet.as_manager()

    def __str__(self):
        return f'{self.address}'
    
