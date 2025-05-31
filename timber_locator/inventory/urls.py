# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                   views.CategoryList.as_view(), name='category-list'),
    path('cat/<slug:slug>/',   views.CategoryDetail.as_view(), name='category-detail'),
    path('profile/<int:pk>/',  views.ProfileDetail.as_view(),  name='profile-detail'),
    path('product/<int:pk>/',  views.ProductDetail.as_view(),  name='product-detail'),
]