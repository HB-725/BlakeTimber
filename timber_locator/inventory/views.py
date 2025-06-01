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
    """AJAX endpoint for product search with fuzzy matching"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'products': []})
    
    # Split search query into individual terms for fuzzy matching
    search_terms = [term.strip() for term in query.split() if term.strip()]
    
    if not search_terms:
        return JsonResponse({'products': []})
    
    # Start with all products
    products = Product.objects.select_related('profile', 'category', 'profile__category')
    
    # Create a comprehensive OR filter that searches across all fields for any term
    # This makes the search much more flexible and user-friendly
    master_filter = Q()
    
    for term in search_terms:
        term_filter = (
            Q(option__icontains=term) |
            Q(profile__name__icontains=term) |
            Q(category__name__icontains=term) |
            Q(profile__category__name__icontains=term) |
            Q(note__icontains=term)
        )
        master_filter |= term_filter
    
    # Apply the combined filter
    products = products.filter(master_filter)
    
    # Limit results and convert to list
    products = list(products[:100])  # Get more results for better scoring
    
    # Score and sort results by relevance
    def calculate_relevance_score(product, search_terms):
        score = 0
        
        # Get all searchable text for this product (excluding I/N number, price, image_url)
        # Priority order: category > profile > option > note
        category_text = ''
        profile_text = ''
        option_text = product.option or ''
        note_text = product.note or ''
        
        # Get category text (highest priority)
        if product.category:
            category_text = product.category.name
        elif product.profile and product.profile.category:
            category_text = product.profile.category.name
            
        # Get profile text (second highest priority)
        if product.profile:
            profile_text = product.profile.name
        
        # Track matches for bonus calculation
        exact_category_matches = 0
        exact_profile_matches = 0
        exact_option_matches = 0
        exact_note_matches = 0
        
        partial_category_matches = 0
        partial_profile_matches = 0
        partial_option_matches = 0
        partial_note_matches = 0
        
        for term in search_terms:
            term_lower = term.lower().strip()
            
            # CATEGORY MATCHES (highest weight - 1000 base)
            if category_text:
                category_lower = category_text.lower()
                category_words = category_lower.split()
                
                # Exact word match in category
                if term_lower in category_words:
                    score += 1000
                    exact_category_matches += 1
                # Partial match in category (much lower but still significant)
                elif term_lower in category_lower:
                    score += 200
                    partial_category_matches += 1
            
            # PROFILE MATCHES (second highest weight - 500 base)
            if profile_text:
                profile_lower = profile_text.lower()
                profile_words = profile_lower.split()
                
                # Exact word match in profile
                if term_lower in profile_words:
                    score += 500
                    exact_profile_matches += 1
                # Partial match in profile
                elif term_lower in profile_lower:
                    score += 100
                    partial_profile_matches += 1
            
            # OPTION MATCHES (third priority - 100 base)
            if option_text:
                option_lower = option_text.lower()
                option_words = option_lower.split()
                
                # Exact word match in option
                if term_lower in option_words:
                    score += 100
                    exact_option_matches += 1
                # Partial match in option
                elif term_lower in option_lower:
                    score += 20
                    partial_option_matches += 1
            
            # NOTE MATCHES (lowest priority - 50 base)
            if note_text:
                note_lower = note_text.lower()
                note_words = note_lower.split()
                
                # Exact word match in note
                if term_lower in note_words:
                    score += 50
                    exact_note_matches += 1
                # Partial match in note
                elif term_lower in note_lower:
                    score += 10
                    partial_note_matches += 1
        
        # MASSIVE bonuses for comprehensive exact matches
        total_terms = len(search_terms)
        total_exact_matches = exact_category_matches + exact_profile_matches + exact_option_matches + exact_note_matches
        
        # Huge bonus if all terms have exact matches somewhere
        if total_exact_matches >= total_terms:
            score += 5000
        
        # Extra bonuses based on where exact matches occur
        if exact_category_matches > 0:
            score += exact_category_matches * 500  # Big bonus for category matches
        if exact_profile_matches > 0:
            score += exact_profile_matches * 250   # Good bonus for profile matches
        if exact_option_matches > 0:
            score += exact_option_matches * 100    # Moderate bonus for option matches
        
        return score
    
    # Score all products and sort by relevance
    scored_products = []
    for product in products:
        score = calculate_relevance_score(product, search_terms)
        if score > 0:  # Only include products with some relevance
            scored_products.append((score, product))
    
    # Sort by score (highest first) and limit to 20 results
    scored_products.sort(key=lambda x: x[0], reverse=True)
    final_products = [product for score, product in scored_products[:20]]
    
    results = []
    for product in final_products:
        results.append({
            'id': product.id,
            'name': product.get_name(),
            'option': product.option or '',
            'in_number': product.in_number,
            'price': str(product.price),
            'note': product.note or '',
            'image_url': product.get_display_image(),
            'url': f'/product/{product.id}/',
            'category': product.get_category().name if product.get_category() else ''
        })
    
    return JsonResponse({'products': results})
