from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Profile, Product

# Custom filters
class ProfileWidthFilter(admin.SimpleListFilter):
    title = 'Width Range'
    parameter_name = 'width_range'

    def lookups(self, request, model_admin):
        return (
            ('small', '70mm and below'),
            ('medium', '90mm - 140mm'),
            ('large', '190mm and above'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'small':
            return queryset.filter(name__startswith='70')
        if self.value() == 'medium':
            return queryset.filter(name__in=['90 x 35mm', '90 x 45mm', '140 x 35mm', '140 x 45mm'])
        if self.value() == 'large':
            return queryset.filter(name__startswith=('190', '240'))

class ProfileLengthFilter(admin.SimpleListFilter):
    title = 'Length Range (Plasterboard)'
    parameter_name = 'plasterboard_length'

    def lookups(self, request, model_admin):
        return (
            ('2400', '2400mm'),
            ('3000', '3000mm'),
            ('3600', '3600mm'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__startswith=self.value())
        return queryset

class ProfileThicknessFilter(admin.SimpleListFilter):
    title = 'Thickness Range (MDF/Sheets)'
    parameter_name = 'mdf_thickness'

    def lookups(self, request, model_admin):
        return (
            ('3mm', '3mm'),
            ('6mm', '6mm'),
            ('9mm', '9mm'),
            ('12mm', '12mm'),
            ('16mm', '16mm'),
            ('18mm', '18mm'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__contains=self.value())
        return queryset


class ProductPriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('budget', 'Under $50'),
            ('moderate', '$50 - $200'),
            ('premium', '$200 - $500'),
            ('expensive', 'Over $500'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'budget':
            return queryset.filter(price__lt=50)
        if self.value() == 'moderate':
            return queryset.filter(price__gte=50, price__lte=200)
        if self.value() == 'premium':
            return queryset.filter(price__gte=200, price__lte=500)
        if self.value() == 'expensive':
            return queryset.filter(price__gt=500)

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'slug', 'get_profile_count', 'has_image')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('level',)
    
    def get_profile_count(self, obj):
        return obj.profile_set.count()
    get_profile_count.short_description = 'Profiles Count'
    
    def has_image(self, obj):
        if obj.image_url:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_image.short_description = 'Has Image'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_dimensions_display', 'get_product_count', 'has_image')
    list_filter = ('category', ProfileWidthFilter, ProfileLengthFilter, ProfileThicknessFilter)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'name')
    list_per_page = 25
    
    def get_dimensions_display(self, obj):
        dimensions = obj.get_dimensions()
        if len(dimensions) == 3:
            return f"{dimensions[0]} x {dimensions[1]} x {dimensions[2]}mm"
        elif len(dimensions) == 2:
            return f"{dimensions[0]} x {dimensions[1]}mm"
        else:
            return "N/A"
    get_dimensions_display.short_description = 'Dimensions'
    
    def get_product_count(self, obj):
        return obj.product_set.count()
    get_product_count.short_description = 'Products Count'
    
    def has_image(self, obj):
        """Show image source with fallback to category"""
        if obj.image_url:
            return format_html('<span style="color: green;">✓ Profile</span>')
        elif obj.category and obj.category.image_url:
            return format_html('<span style="color: orange;">✓ Category</span>')
        else:
            return format_html('<span style="color: red;">✗ None</span>')
    has_image.short_description = 'Image Source'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('in_number', 'get_product_name', 'option', 'price', 'location', 'has_image', 'get_category')
    list_filter = ('category', 'profile__category', 'profile', 'location', ProductPriceRangeFilter)
    search_fields = ('in_number', 'profile__name', 'category__name', 'profile__category__name', 'location', 'option')
    ordering = ('category', 'profile__category', 'profile__name', 'option')
    list_per_page = 50
    list_editable = ('option', 'price', 'location')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('in_number',),
        }),
        ('Product Classification', {
            'fields': ('category', 'profile'),
            'description': 'Choose either a category (for direct products) OR a profile (for profile-based products).'
        }),
        ('Product Options', {
            'fields': ('option',),
            'description': 'Specify product dimensions, length, or other specifications (e.g., "3.6 m", "2400x1200mm", "4x8 feet") - REQUIRED'
        }),
        ('Pricing & Location', {
            'fields': ('price', 'location')
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
    )
    
    def get_product_name(self, obj):
        return obj.get_name()
    get_product_name.short_description = 'Product Name'
    
    def get_dimension_display(self, obj):
        return obj.get_dimension_display()
    get_dimension_display.short_description = 'Dimensions'
    
    def get_category(self, obj):
        category = obj.get_category()
        return category.name if category else "No Category"
    get_category.short_description = 'Category'
    
    def has_image(self, obj):
        """Show image source with fallback hierarchy: Product -> Profile -> Category"""
        if obj.image_url:
            return format_html('<span style="color: green;">✓ Product</span>')
        elif obj.profile and obj.profile.image_url:
            return format_html('<span style="color: blue;">✓ Profile</span>')
        elif obj.profile and obj.profile.category and obj.profile.category.image_url:
            return format_html('<span style="color: orange;">✓ Category</span>')
        elif obj.category and obj.category.image_url:
            return format_html('<span style="color: orange;">✓ Category</span>')
        else:
            return format_html('<span style="color: red;">✗ None</span>')
    has_image.short_description = 'Image Source'
