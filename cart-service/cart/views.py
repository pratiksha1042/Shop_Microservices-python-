from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

PRODUCT_SERVICE_URL = "http://127.0.0.1:8001//products/"

class CartListView(APIView):
    def get(self, request, user_id):
        try:
            cart = Cart.objects.get(user_id=user_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

class CartItemAddView(APIView):
    def post(self, request, user_id):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        # Get product details from Product Service
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}/")
        
        if response.status_code != 200:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        product_data = response.json()
        product_name = product_data.get("name")
        price = product_data.get("price")

        # Add item to cart
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        cart_item = CartItem.objects.create(
            cart=cart, 
            product_id=product_id, 
            product_name=product_name, 
            quantity=quantity, 
            price=price
        )

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

class CartItemRemoveView(APIView):
    def delete(self, request, user_id, item_id):
        try:
            cart = Cart.objects.get(user_id=user_id)
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

