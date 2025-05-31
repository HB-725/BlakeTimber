# inventory/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
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
            # Get all profiles for this category, sorted by width numerically
            profiles = Profile.objects.filter(category=self.object)
            context['profiles'] = sorted(profiles, key=lambda profile: profile.get_width())
            logger.debug(f"Profiles: {context['profiles']}")
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
        # Get all products with the same profile, including current product
        context['all_products'] = Product.objects.filter(
            profile=self.object.profile
        ).order_by('length', 'size')
        return context
