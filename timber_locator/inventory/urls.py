# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                   views.HomePage.as_view(), name='home-page'),
    path('cat/<slug:slug>/',   views.CategoryDetail.as_view(), name='category-detail'),
    path('profile/<int:pk>/',  views.ProfileDetail.as_view(),  name='profile-detail'),
    path('profile/<int:pk>/empty/', views.profile_empty, name='profile-empty'),
    path('product/<int:pk>/',  views.ProductDetail.as_view(),  name='product-detail'),
    path('search-page/',       views.SearchPage.as_view(),    name='search-page'),
    path('tools/specrite/',    views.SpecRiteCalculatorPage.as_view(), name='specrite-calculator'),
    path('search/',            views.search_products, name='search-products'),
    path('add/category/',      views.add_category, name='add-category'),
    path('add/profile/',       views.add_profile, name='add-profile'),
    path('add/product/',       views.add_product, name='add-product'),
    path('edit/category/<int:pk>/', views.edit_category, name='edit-category'),
    path('delete/category/<int:pk>/', views.delete_category, name='delete-category'),
    path('edit/profile/<int:pk>/', views.edit_profile, name='edit-profile'),
    path('delete/profile/<int:pk>/', views.delete_profile, name='delete-profile'),
    path('edit/product/<int:pk>/', views.edit_product, name='edit-product'),
    path('delete/product/<int:pk>/', views.delete_product, name='delete-product'),
    path('modal/clear/',       views.modal_clear, name='modal-clear'),
    path('ajax/login/',        views.ajax_login, name='ajax-login'),
    path('ajax/logout/',       views.ajax_logout, name='ajax-logout'),
    path('admin-mode/',        views.enter_admin_mode, name='admin-mode'),
    path('admin-mode/exit/',   views.exit_admin_mode, name='admin-mode-exit'),
]
