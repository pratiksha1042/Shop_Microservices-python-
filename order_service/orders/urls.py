from django.urls import path
from .views import CreateOrderView, OrderListView

urlpatterns = [
    path('orders/<int:user_id>/', OrderListView.as_view(), name='order-list'),
    path('orders/create/<int:user_id>/', CreateOrderView.as_view(), name='order-create'),
]
