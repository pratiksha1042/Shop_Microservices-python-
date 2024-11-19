from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from decimal import Decimal
import requests

CART_SERVICE_URL = "http://127.0.0.1:8002/api/cart/"
PRODUCT_SERVICE_URL = "http://127.0.0.1:8001/api/products/"

class CreateOrderView(APIView):
    def post(self, request, user_id):
        # Fetch cart details from Cart Service
        cart_response = requests.get(f"{CART_SERVICE_URL}{user_id}/")
        if cart_response.status_code != 200:
            return Response({"error": "Unable to fetch cart details"}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = cart_response.json()
        items = cart_data.get("items", [])
        if not items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock and calculate total amount
        total_amount = Decimal('0.00')  # Initialize as a Decimal type
        for item in items:
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}{item['product_id']}/")
            if product_response.status_code != 200:
                return Response({"error": f"Product {item['product_id']} not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            product_data = product_response.json()
            if item["quantity"] > product_data["stock"]:
                return Response({"error": f"Insufficient stock for product {product_data['name']}"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure price is a Decimal type
            price = Decimal(str(item["price"]))  # Convert price to Decimal

            total_amount += item["quantity"] * price

        # Create Order
        order = Order.objects.create(user_id=user_id, total_amount=total_amount)
        for item in items:
            # Ensure price is a Decimal type when creating OrderItem
            price = Decimal(str(item["price"]))  # Convert price to Decimal
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                price=price,
            )
            # Update stock in Product Service
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}{item['product_id']}/")
            product_data = product_response.json()
            updated_stock = product_data["stock"] - item["quantity"]
            requests.patch(f"{PRODUCT_SERVICE_URL}{item['product_id']}/", data={"stock": updated_stock})

        # Clear user's cart
        requests.delete(f"{CART_SERVICE_URL}{user_id}/")

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

class OrderListView(APIView):
    def get(self, request, user_id):
        orders = Order.objects.filter(user_id=user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
