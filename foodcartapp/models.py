from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

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
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

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
            models.F('product_position__current_price') \
                * models.F('product_position__quantity'),
            output_field=models.DecimalField()
        )

        return self.annotate(
            total=models.Sum(subtotal)
        )


class Order(models.Model):
    STATUSES = [
        ('N', 'Новый'),
        ('P', 'В работе'),
        ('C', 'Выполнен')
    ]
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    phonenumber = PhoneNumberField()
    address = models.TextField()
    products = models.ManyToManyField(Product, through='OrderPosition')
    status = models.CharField('Статус', max_length=2, choices=STATUSES, default='N')
    comment = models.TextField('Комментарий', blank=True)

    objects = OrderQuerySet.as_manager()
    
    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    

class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Заказ',
        related_name='product_position'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Товар'
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