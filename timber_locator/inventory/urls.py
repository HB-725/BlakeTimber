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
    path('add/category/',      views.add_category, name='add-category'),
    path('add/profile/',       views.add_profile, name='add-profile'),
    path('add/product/',       views.add_product, name='add-product'),
    path('ajax/login/',        views.ajax_login, name='ajax-login'),
    path('ajax/logout/',       views.ajax_logout, name='ajax-logout'),
    path('admin-mode/',        views.enter_admin_mode, name='admin-mode'),
    path('admin-mode/exit/',   views.exit_admin_mode, name='admin-mode-exit'),
]
