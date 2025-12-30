# inventory/views.py
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from .models import Category, Profile, Product
import logging
import re

logger = logging.getLogger(__name__)

class HomePage(ListView):
    model = Category
    template_name = 'inventory/HomePage.html'
    queryset = Category.objects.filter(parent__isnull=True)

class CategoryDetail(DetailView):
    model = Category
    template_name = 'inventory/CategoryPage.html'
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
    template_name = 'inventory/ProductPage.html'

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


class SearchPage(TemplateView):
    template_name = 'inventory/SearchPage.html'


@require_POST
def ajax_login(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'ok': False, 'error': 'Invalid username or password.'}, status=400)
    login(request, user)
    return JsonResponse({'ok': True})


@require_POST
def ajax_logout(request):
    logout(request)
    return JsonResponse({'ok': True})




def search_products(request):
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'products': [], 'profiles': [], 'categories': []})

    raw_terms = [term for term in query.split() if term]

    def term_variants(term):
        variants = {term}
        cleaned = term.lower().replace('×', 'x')
        variants.add(cleaned)
        digits_only = ''.join(ch for ch in cleaned if ch.isdigit())
        if digits_only:
            variants.add(digits_only)
        if cleaned.endswith('mm'):
            variants.add(cleaned[:-2])
        elif cleaned.endswith('m'):
            variants.add(cleaned[:-1])
        if 'x' in cleaned:
            variants.add(cleaned.replace('x', ' x '))
        return [v for v in variants if v]

    def term_unit(term):
        cleaned = term.lower().replace('×', 'x')
        if cleaned.endswith('mm'):
            return 'mm'
        if cleaned.endswith('m'):
            return 'm'
        return ''

    search_terms = raw_terms

    product_filter = Q()
    for term in search_terms:
        variants = term_variants(term)
        unit = term_unit(term)
        term_filter = Q()
        for variant in variants:
            if unit == 'm':
                term_filter |= (
                    Q(option__icontains=variant) |
                    Q(note__icontains=variant)
                )
            else:
                term_filter |= (
                    Q(option__icontains=variant) |
                    Q(note__icontains=variant) |
                    Q(profile__name__icontains=variant) |
                    Q(category__name__icontains=variant) |
                    Q(profile__category__name__icontains=variant)
                )
        product_filter &= term_filter

    products = Product.objects.select_related(
        'category',
        'profile',
        'profile__category'
    ).filter(product_filter).distinct()[:50]

    profile_filter = Q()
    for term in search_terms:
        if term_unit(term) == 'm':
            continue
        variants = term_variants(term)
        term_filter = Q()
        for variant in variants:
            term_filter |= (
                Q(name__icontains=variant) |
                Q(category__name__icontains=variant)
            )
        profile_filter &= term_filter

    profiles = Profile.objects.select_related('category').filter(profile_filter).distinct()[:30]

    category_filter = Q()
    for term in search_terms:
        if term_unit(term) == 'm':
            continue
        variants = term_variants(term)
        term_filter = Q()
        for variant in variants:
            term_filter |= Q(name__icontains=variant)
        category_filter &= term_filter

    categories = Category.objects.filter(category_filter).distinct()[:30]

    def normalize_keep_x(value):
        return ''.join(
            ch for ch in value.lower().replace('×', 'x')
            if ch.isalnum() or ch == 'x'
        )

    def normalize_digits(value):
        return ''.join(ch for ch in value.lower() if ch.isalnum())

    query_with_x = normalize_keep_x('x'.join(search_terms))
    query_compact = normalize_digits(''.join(search_terms))
    query_numbers = [int(term) for term in search_terms if term.isdigit()]

    def extract_numbers(value):
        return [int(match) for match in re.findall(r'\d+', value)]

    def extract_numbers_float(value):
        return [float(match) for match in re.findall(r'\d+(?:\.\d+)?', value)]

    def score_product(product):
        option_text = product.option or ''
        profile_text = product.profile.name if product.profile else ''
        category_text = product.get_category().name if product.get_category() else ''

        option_norm = normalize_keep_x(option_text)
        profile_norm = normalize_keep_x(profile_text)
        category_norm = normalize_keep_x(category_text)
        option_compact = normalize_digits(option_text)
        profile_compact = normalize_digits(profile_text)

        score = 0
        if len(query_numbers) >= 2:
            target_first, target_second = query_numbers[0], query_numbers[1]
            source_text = option_text or profile_text
            item_numbers = extract_numbers(source_text)
            if len(item_numbers) >= 2:
                item_first, item_second = item_numbers[0], item_numbers[1]
                if item_first == target_first and item_second == target_second:
                    score += 20000
                elif item_second == target_second:
                    score += max(0, 12000 - abs(item_first - target_first) * 10)
        if len(query_numbers) >= 3:
            target_third = float(query_numbers[2])
            option_numbers = extract_numbers_float(option_text)
            if len(option_numbers) >= 1:
                option_last = option_numbers[-1]
                if abs(option_last - target_third) < 0.01:
                    score += 15000
                else:
                    score += max(0, 6000 - abs(option_last - target_third) * 1000)
        if query_with_x and query_with_x in option_norm:
            score += 1000
        if query_with_x and query_with_x in profile_norm:
            score += 800
        if query_compact and query_compact in option_compact:
            score += 700
        if query_compact and query_compact in profile_compact:
            score += 600
        if query_with_x and query_with_x in category_norm:
            score += 200
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in option_text.lower():
                score += 40
            if term_lower in profile_text.lower():
                score += 30
            if term_lower in category_text.lower():
                score += 10
        return score

    products = sorted(list(products), key=score_product, reverse=True)

    def product_payload(product):
        category = product.category or (product.profile.category if product.profile else None)
        return {
            'id': product.id,
            'name': product.get_name(),
            'option': product.get_dimension_display(),
            'category': category.name if category else '',
            'profile': product.profile.name if product.profile else '',
            'price': str(product.price) if product.price is not None else '',
            'image_url': product.get_display_image() or '',
            'in_number': product.in_number,
        }

    return JsonResponse({
        'products': [product_payload(product) for product in products],
        'profiles': [
            {
                'id': profile.id,
                'name': profile.name,
                'category': profile.category.name,
                'category_slug': profile.category.slug,
            }
            for profile in profiles
        ],
        'categories': [
            {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
            }
            for category in categories
        ],
    })
