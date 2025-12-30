from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
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


class ProductCategoryFilter(admin.SimpleListFilter):
    title = 'Category'
    parameter_name = 'category_filter'

    def lookups(self, request, model_admin):
        # Get all categories that are used by products (either directly or through profiles)
        from django.db.models import Q
        categories = Category.objects.filter(
            Q(product__isnull=False) | Q(profile__product__isnull=False)
        ).distinct().order_by('name')
        
        return [(cat.id, cat.name) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            # Filter products that have this category either directly or through profile
            from django.db.models import Q
            return queryset.filter(
                Q(category_id=self.value()) | Q(profile__category_id=self.value())
            )

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
    list_display = ('in_number', 'get_product_name', 'option', 'note', 'has_image', 'get_category')
    list_filter = (ProductCategoryFilter, 'profile', 'note')
    search_fields = ('in_number', 'profile__name', 'category__name', 'profile__category__name', 'note', 'option')
    ordering = ('profile__category', 'profile__name', 'option')
    list_per_page = 50
    list_editable = ('option', 'note')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='inventory_product_bulk_create'),
        ]
        return custom_urls + urls
    
    def bulk_create_view(self, request):
        """Custom view for bulk creating products"""
        context = {
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'title': 'Bulk Create Products',
        }
        
        if request.method == 'POST':
            # Get the selected category or profile
            category_id = request.POST.get('category')
            profile_id = request.POST.get('profile')
            product_count = int(request.POST.get('product_count', 0))
            
            # Validate that either category or profile is selected
            if not category_id and not profile_id:
                messages.error(request, 'Please select either a category or profile.')
                context.update({
                    'categories': Category.objects.all().order_by('name'),
                    'profiles': Profile.objects.all().order_by('category__name', 'name'),
                })
                return render(request, 'admin/inventory/bulk_create_products.html', context)
            
            if category_id and profile_id:
                messages.error(request, 'Please select only one - either category OR profile.')
                context.update({
                    'categories': Category.objects.all().order_by('name'),
                    'profiles': Profile.objects.all().order_by('category__name', 'name'),
                })
                return render(request, 'admin/inventory/bulk_create_products.html', context)
            
            if product_count == 0:
                messages.error(request, 'Please add at least one product.')
                context.update({
                    'categories': Category.objects.all().order_by('name'),
                    'profiles': Profile.objects.all().order_by('category__name', 'name'),
                    'selected_category': category_id,
                    'selected_profile': profile_id,
                })
                return render(request, 'admin/inventory/bulk_create_products.html', context)
            
            # Process the product data
            try:
                created_count = 0
                errors = []
                category = Category.objects.get(id=category_id) if category_id else None
                profile = Profile.objects.get(id=profile_id) if profile_id else None
                
                for i in range(product_count):
                    option = request.POST.get(f'product_{i}_option', '').strip()
                    in_number = request.POST.get(f'product_{i}_in_number', '').strip()
                    note = request.POST.get(f'product_{i}_note', '').strip()
                    image_url = request.POST.get(f'product_{i}_image_url', '').strip()
                    
                    # Skip empty rows
                    if not option and not in_number:
                        continue
                    
                    # Validate required fields
                    if not option:
                        errors.append(f'Product {i+1}: Option is required')
                        continue
                    if not in_number:
                        errors.append(f'Product {i+1}: I/N Number is required')
                        continue
                    # Check for duplicate I/N numbers
                    if Product.objects.filter(in_number=in_number).exists():
                        errors.append(f'Product {i+1}: I/N Number "{in_number}" already exists')
                        continue
                    
                    # Create the product
                    product = Product(
                        category=category,
                        profile=profile,
                        option=option,
                        in_number=in_number,
                        note=note,
                        image_url=image_url
                    )
                    product.save()
                    created_count += 1
                
                if errors:
                    for error in errors:
                        messages.error(request, error)
                
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} products.')
                    if not errors:  # Only redirect if no errors
                        return HttpResponseRedirect(reverse('admin:inventory_product_changelist'))
                elif not errors:
                    messages.warning(request, 'No products were created.')
                    
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
            
            # If there were errors, re-populate context
            context.update({
                'categories': Category.objects.all().order_by('name'),
                'profiles': Profile.objects.all().order_by('category__name', 'name'),
                'selected_category': category_id,
                'selected_profile': profile_id,
            })
            return render(request, 'admin/inventory/bulk_create_products.html', context)
        else:
            # GET request - show the form
            context.update({
                'categories': Category.objects.all().order_by('name'),
                'profiles': Profile.objects.all().order_by('category__name', 'name'),
            })
        
        return render(request, 'admin/inventory/bulk_create_products.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to add bulk create button"""
        extra_context = extra_context or {}
        extra_context['bulk_create_url'] = reverse('admin:inventory_product_bulk_create')
        return super().changelist_view(request, extra_context)
    
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
        ('Notes', {
            'fields': ('note',)
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
