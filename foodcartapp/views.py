import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer


from .models import Product
from .models import Order, OrderPosition, RestaurantMenuItem

def get_product_restaurant(product):
    menu_items = RestaurantMenuItem.objects \
        .prefetch_related('product') \
        .filter(availability=True) \
        .order_by('product') \
        .values_list('product', 'restaurant')

    return set(rest for prod, rest in list(menu_items) if prod==product.id)

class OrderPositionSerializer(ModelSerializer):
    class Meta:
        model = OrderPosition
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderPositionSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    from pprint import pprint
    raw_order = request.data
    # pprint(raw_order)
    required_keys = [
        'address', 'firstname', 'lastname', 'phonenumber', 'products'
    ]
    serializer = OrderSerializer(data=raw_order)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    products_fields = list(validated_data['products'])

    # for product in products_fields:
    #     print(product['product'].id)
    
    for field in products_fields:
        field['current_price'] = field['product'].price
    # pprint(
    #     get_product_restaurant(products_fields[0]['product'].id)
    # )

    

    order = Order.objects.create(
        address=validated_data['address'],
        firstname=validated_data['firstname'],
        lastname=validated_data['lastname'],
        phonenumber=validated_data['phonenumber'],
    )




    products = [
        OrderPosition(order=order, **fields) for fields in products_fields
    ]
    
    OrderPosition.objects.bulk_create(products)
    response = OrderSerializer(instance=order)
    
    return Response(response.data)

