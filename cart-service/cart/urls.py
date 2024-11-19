from django.urls import path
from .views import CartListView, CartItemAddView, CartItemRemoveView

urlpatterns = [
    path('cart/<int:user_id>/', CartListView.as_view(), name='cart-list'),
    path('cart/<int:user_id>/add/', CartItemAddView.as_view(), name='cart-item-add'),
    path('cart/<int:user_id>/remove/<int:item_id>/', CartItemRemoveView.as_view(), name='cart-item-remove'),
]
    