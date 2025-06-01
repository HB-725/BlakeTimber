# inventory/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Profile, Product
import logging

logger = logging.getLogger(__name__)

class CategoryList(ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    queryset = Category.objects.filter(parent__isnull=True)

class CategoryDetail(DetailView):
    model = Category
    template_name = 'inventory/category_details.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        """Check if category has profiles or only direct products"""
        self.object = self.get_object()
        
        # Get profiles and direct products for this category
        profiles = Profile.objects.filter(category=self.object)
        direct_products = Product.objects.filter(category=self.object, profile__isnull=True)
        
        # If no profiles exist but direct products do, redirect to first product
        if not profiles.exists() and direct_products.exists():
            first_product = direct_products.first()
            return redirect('product-detail', pk=first_product.pk)
        
        # Otherwise, show the category detail page normally
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            logger.debug(f"Category object: {self.object}")
            # Get all children categories
            context['children'] = self.object.get_children()
            logger.debug(f"Children: {context['children']}")
            
            # Get all profiles for this category, sorted appropriately
            profiles = Profile.objects.filter(category=self.object)
            
            # Get direct products for this category (not through profiles)
            direct_products = Product.objects.filter(category=self.object, profile__isnull=True)
            
            # Sort profiles based on category type
            if 'plasterboard' in self.object.name.lower():
                # For plasterboard, sort by length (first dimension)
                print(f"Sorting plasterboard category: {self.object.name}")
                context['profiles'] = sorted(profiles, key=lambda profile: profile.get_length())
                print(f"Sorted profiles: {[p.name for p in context['profiles']]}")
            elif 'mdf' in self.object.name.lower():
                # For MDF, sort by thickness (third dimension)
                print(f"Sorting MDF category: {self.object.name}")
                context['profiles'] = sorted(profiles, key=lambda profile: profile.get_thickness())
                print(f"Sorted profiles: {[p.name for p in context['profiles']]}")
            else:
                # For timber and other categories, sort by width (first dimension)
                print(f"Sorting timber category: {self.object.name}")
                context['profiles'] = sorted(profiles, key=lambda profile: profile.get_width())
            
            # Add direct products to context
            context['direct_products'] = direct_products.order_by('option')
            
            logger.debug(f"Profiles: {context['profiles']}")
            logger.debug(f"Direct products: {context['direct_products']}")
            return context
        except Exception as e:
            logger.error(f"Error in CategoryDetail.get_context_data: {str(e)}", exc_info=True)
            raise

class ProfileDetail(DetailView):
    model = Profile
    
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        # Get the first product for this profile
        first_product = profile.product_set.first()
        if first_product:
            return redirect('product-detail', pk=first_product.pk)
        else:
            # If no products exist, redirect back to category
            return redirect('category-detail', slug=profile.category.slug)

class ProductDetail(DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all products with the same classification (either profile-based or category-based)
        if self.object.profile:
            # If this product has a profile, get all products with the same profile
            context['all_products'] = Product.objects.filter(
                profile=self.object.profile
            ).order_by('option')
        else:
            # If this product is directly linked to category, get all direct products in same category
            context['all_products'] = Product.objects.filter(
                category=self.object.category,
                profile__isnull=True
            ).order_by('option')
        
        return context

def search_products(request):
    """AJAX endpoint for product search"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'products': []})
    
    # Search across multiple fields
    products = Product.objects.filter(
        Q(in_number__icontains=query) |
        Q(option__icontains=query) |
        Q(profile__name__icontains=query) |
        Q(category__name__icontains=query) |
        Q(profile__category__name__icontains=query) |
        Q(location__icontains=query)
    ).select_related('profile', 'category', 'profile__category')[:20]  # Limit to 20 results
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.get_name(),
            'option': product.option or '',
            'in_number': product.in_number,
            'price': str(product.price),
            'location': product.location or '',
            'image_url': product.get_display_image(),
            'url': f'/product/{product.id}/',
            'category': product.get_category().name if product.get_category() else ''
        })
    
    return JsonResponse({'products': results})
