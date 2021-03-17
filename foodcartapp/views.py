import json

from django.http import JsonResponse
from django.templatetags.static import static


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


def register_order(request):
    # TODO это лишь заглушка
    from pprint import pprint
    raw_order = json.loads(request.body.decode())
    order_positions = raw_order.pop('products')
    order = Order.objects.create(**raw_order)
    
    for position in order_positions:
        pprint(position)
        product = {
            'product': Product.objects.get(id=position['product']),
            'order': order,
            'quantity': position['quantity']
        }
        OrderPosition.objects.create(**product)
    
    pprint(raw_order)
    return JsonResponse({})
