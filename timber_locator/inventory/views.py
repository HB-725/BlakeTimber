from django.shortcuts import render, get_object_or_404

# inventory/views.py
from django.views.generic import ListView, DetailView
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

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            logger.debug(f"Category object: {self.object}")
            # Get all children categories
            context['children'] = self.object.get_children()
            logger.debug(f"Children: {context['children']}")
            # Get all profiles for this category
            context['profiles'] = Profile.objects.filter(category=self.object)
            logger.debug(f"Profiles: {context['profiles']}")
            return context
        except Exception as e:
            logger.error(f"Error in CategoryDetail.get_context_data: {str(e)}", exc_info=True)
            raise

class ProfileDetail(DetailView):
    model = Profile
    template_name = 'inventory/profile_detail.html'

class ProductDetail(DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get other products with the same profile, excluding current product
        context['other_lengths'] = Product.objects.filter(
            profile=self.object.profile
        ).exclude(
            id=self.object.id
        ).order_by('length')
        return context

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

def profile_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    profiles = list(Profile.objects.filter(category=category))
    # Sort profiles by dimensions (width, then height)
    profiles.sort(key=lambda p: p.get_dimensions())
    return render(request, 'inventory/profile_list.html', {
        'category': category,
        'profiles': profiles
    })

def product_list(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    products = Product.objects.filter(profile=profile)
    return render(request, 'inventory/product_list.html', {
        'profile': profile,
        'products': products
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'inventory/product_detail.html', {'product': product})
