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


class ProductLengthFilter(admin.SimpleListFilter):
    title = 'Length Range'
    parameter_name = 'length_range'

    def lookups(self, request, model_admin):
        return (
            ('short', 'Under 3m'),
            ('medium', '3m - 6m'),
            ('long', 'Over 6m'),
            ('no_length', 'No length specified'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(length__lt=3, length__isnull=False)
        if self.value() == 'medium':
            return queryset.filter(length__gte=3, length__lte=6)
        if self.value() == 'long':
            return queryset.filter(length__gt=6)
        if self.value() == 'no_length':
            return queryset.filter(length__isnull=True)

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
    list_display = ('name', 'category', 'get_width_display', 'get_height_display', 'get_product_count', 'has_image')
    list_filter = ('category', ProfileWidthFilter)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'name')
    list_per_page = 25
    
    def get_width_display(self, obj):
        width, _ = obj.get_dimensions()
        return f"{width}mm" if width > 0 else "N/A"
    get_width_display.short_description = 'Width'
    get_width_display.admin_order_field = 'name'
    
    def get_height_display(self, obj):
        _, height = obj.get_dimensions()
        return f"{height}mm" if height > 0 else "N/A"
    get_height_display.short_description = 'Height'
    
    def get_product_count(self, obj):
        return obj.product_set.count()
    get_product_count.short_description = 'Products Count'
    
    def has_image(self, obj):
        if obj.image_url:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_image.short_description = 'Has Image'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('in_number', 'profile', 'get_dimension_display', 'price', 'location', 'has_image', 'get_category')
    list_filter = ('profile__category', 'profile', ProductLengthFilter, 'location')
    search_fields = ('in_number', 'profile__name', 'profile__category__name', 'location')
    ordering = ('profile__category', 'profile__name', 'length', 'size')
    list_per_page = 50
    list_editable = ('price', 'location')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'in_number')
        }),
        ('Dimensions', {
            'fields': ('length', 'size'),
            'description': 'Specify either length (for lumber) or size (for sheets/panels)'
        }),
        ('Pricing & Location', {
            'fields': ('price', 'location')
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
    )
    
    def get_dimension_display(self, obj):
        return obj.get_dimension_display()
    get_dimension_display.short_description = 'Dimensions'
    
    def get_category(self, obj):
        return obj.profile.category.name
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'profile__category__name'
    
    def has_image(self, obj):
        if obj.image_url or obj.profile.image_url:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_image.short_description = 'Has Image'
