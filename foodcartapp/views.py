import json

from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product
from .models import Order, OrderPosition


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

@api_view(['POST'])
def register_order(request):
    from pprint import pprint
    raw_order = request.data
    required_keys = ['address', 'firstname', 'lastname', 'phonenumber', 'products']
    print(raw_order)
    order_ok = all(key in raw_order.keys() for key in required_keys) \
        and all(raw_order[key] for key in raw_order.keys()) \
        and isinstance(raw_order['products'], list) \
        and all(isinstance(raw_order[key], str) for key in required_keys[:4]) \
        and all(isinstance(product['product'], int) for product in raw_order['products']) \
        and all(Product.objects.filter(id=product['product']) for product in raw_order['products'])
    print(order_ok)

    if not order_ok:
        return Response(
            {'status': 'error'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    order_positions = raw_order.pop('products')
    order = Order.objects.create(**raw_order)

    for position in order_positions:
        product = {
            'product': Product.objects.get(id=position['product']),
            'order': order,
            'quantity': position['quantity']
        }
        OrderPosition.objects.create(**product)
    
    return Response({
        'status': 'ok'
    })


