# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                   views.HomePage.as_view(), name='home-page'),
    path('cat/<slug:slug>/',   views.CategoryDetail.as_view(), name='category-detail'),
    path('profile/<int:pk>/',  views.ProfileDetail.as_view(),  name='profile-detail'),
    path('product/<int:pk>/',  views.ProductDetail.as_view(),  name='product-detail'),
    path('search-page/',       views.SearchPage.as_view(),    name='search-page'),
    path('search/',            views.search_products, name='search-products'),
    path('ajax/login/',        views.ajax_login, name='ajax-login'),
    path('ajax/logout/',       views.ajax_logout, name='ajax-logout'),
]
