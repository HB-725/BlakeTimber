from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Profile, Product

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter  = ('category',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('in_number', 'profile', 'length', 'price', 'location')
    list_filter    = ('profile__category',)
    search_fields  = ('in_number', 'profile__name')
