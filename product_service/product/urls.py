from django.urls import path
from .views import ProductListView, ProductCreateView,ProductDetailView
from . import views 
urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),  # Fixed path

]
