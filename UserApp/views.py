
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale, SaleItem
from django.db import transaction
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

cart = {}

def product_list(request):
    products = Product.objects.all()

    data = [
        {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "stock": product.stock,
        }
        for product in products
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product_id in cart:
        cart[product_id]["qty"] += 1
    else:
        cart[product_id] = {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "qty": 1,
        }

    return JsonResponse({
        "success": True,
        "message": "Product added to cart"
    })

def view_cart(request):

    items = []
    total = 0

    for product_id, item in cart.items():

        subtotal = item["price"] * item["qty"]

        items.append({
            "id": product_id,
            "name": item["name"],
            "price": item["price"],
            "quantity": item["qty"],
            "subtotal": subtotal,
        })

        total += subtotal

    return JsonResponse({
        "items": items,
        "total": total,
    })

@csrf_exempt
def update_cart(request, product_id):

    data = json.loads(request.body)

    qty = int(data.get("quantity", 1))

    if product_id in cart:
        cart[product_id]["qty"] = qty

    return JsonResponse({
        "success": True,
        "message": "Cart updated"
    })

@csrf_exempt
def remove_from_cart(request, product_id):

    if product_id in cart:
        del cart[product_id]

    return JsonResponse({
        "success": True,
        "message": "Item removed"
    })

@csrf_exempt
@transaction.atomic
def checkout(request):

    if not cart:
        return JsonResponse({
            "success": False,
            "message": "Cart is empty"
        }, status=400)

    total = sum(
        item["price"] * item["qty"]
        for item in cart.values()
    )

    sale = Sale.objects.create(
        total_amount=total
    )

    for pid, item in cart.items():

        product = Product.objects.get(id=pid)

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=item["qty"],
            price=item["price"],
            subtotal=item["qty"] * item["price"]
        )

        product.stock -= item["qty"]
        product.save()

    cart.clear()

    return JsonResponse({
        "success": True,
        "message": "Sale completed",
        "sale_id": sale.id,
    })

def sales_history(request):

    sales = Sale.objects.prefetch_related(
        "items__product"
    ).order_by("-created_at")

    data = []

    for sale in sales:

        sale_items = []

        for item in sale.items.all():
            sale_items.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": float(item.price),
                "subtotal": float(item.subtotal),
            })

        data.append({
            "id": sale.id,
            "total_amount": float(sale.total_amount),
            "created_at": sale.created_at,
            "items_count": sale.items.count(),
            "items": sale_items,
        })

    return JsonResponse(data, safe=False)