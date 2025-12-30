from django import forms
from django.forms import formset_factory, BaseFormSet
from .models import Category, Profile, Product

BASE_INPUT_CLASS = "w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/30"
BASE_SELECT_CLASS = "w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/30"

class CategoryForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": BASE_INPUT_CLASS,
            "accept": "image/jpeg,image/png,image/webp,image/gif",
            "data-image-input": "true"
        })
    )

    class Meta:
        model = Category
        fields = ["name", "image_file", "image_url", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "Category name"}),
            "image_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "Optional image URL"}),
            "parent": forms.Select(attrs={"class": BASE_SELECT_CLASS}),
        }

    def clean_image_file(self):
        image = self.cleaned_data.get("image_file")
        if not image:
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type.startswith("image/"):
            raise forms.ValidationError("Please upload an image file.")
        allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if content_type not in allowed:
            raise forms.ValidationError("Only JPG, PNG, WEBP, or GIF images are allowed.")
        return image


class ProfileForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": BASE_INPUT_CLASS,
            "accept": "image/jpeg,image/png,image/webp,image/gif",
            "data-image-input": "true"
        })
    )

    class Meta:
        model = Profile
        fields = ["category", "name", "image_file", "image_url"]
        widgets = {
            "category": forms.Select(attrs={"class": BASE_SELECT_CLASS}),
            "name": forms.TextInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "e.g. 90 x 35mm"}),
            "image_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "Optional image URL"}),
        }

    def clean_image_file(self):
        image = self.cleaned_data.get("image_file")
        if not image:
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type.startswith("image/"):
            raise forms.ValidationError("Please upload an image file.")
        allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if content_type not in allowed:
            raise forms.ValidationError("Only JPG, PNG, WEBP, or GIF images are allowed.")
        return image


class ProductForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": BASE_INPUT_CLASS,
            "accept": "image/jpeg,image/png,image/webp,image/gif",
            "data-image-input": "true"
        })
    )

    class Meta:
        model = Product
        fields = ["category", "profile", "option", "in_number", "note", "image_file", "image_url"]
        widgets = {
            "category": forms.Select(attrs={"class": BASE_SELECT_CLASS}),
            "profile": forms.Select(attrs={"class": BASE_SELECT_CLASS}),
            "option": forms.TextInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "e.g. 2.4m"}),
            "in_number": forms.TextInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "I/N number"}),
            "note": forms.TextInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "Optional note"}),
            "image_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASS, "placeholder": "Optional image URL"}),
        }

    def clean_image_file(self):
        image = self.cleaned_data.get("image_file")
        if not image:
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type.startswith("image/"):
            raise forms.ValidationError("Please upload an image file.")
        allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if content_type not in allowed:
            raise forms.ValidationError("Only JPG, PNG, WEBP, or GIF images are allowed.")
        return image

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        profile = cleaned_data.get("profile")
        if not category and not profile:
            raise forms.ValidationError("Choose a category or a profile.")
        if category and profile:
            raise forms.ValidationError("Choose either category or profile, not both.")
        return cleaned_data

class BulkProductForm(forms.Form):
    """Form for individual product creation in bulk"""
    option = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'e.g., 2.4m, 3600x1200mm, etc.',
            'style': 'width: 200px;'
        }),
        help_text="Required: dimensions, length, or specifications"
    )
    in_number = forms.CharField(
        max_length=50,
        label="I/N Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Unique identifier',
            'style': 'width: 150px;'
        })
    )
    note = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Optional notes',
            'style': 'width: 200px;'
        })
    )
    image_url = forms.URLField(
        max_length=500,
        required=False,
        label="Image URL",
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Optional image URL',
            'style': 'width: 250px;'
        })
    )

    def clean_in_number(self):
        in_number = self.cleaned_data.get('in_number')
        if in_number and Product.objects.filter(in_number=in_number).exists():
            raise forms.ValidationError(f"I/N Number '{in_number}' already exists.")
        return in_number

class BaseBulkProductFormSet(BaseFormSet):
    def clean(self):
        """Check that at least one form has data"""
        if any(self.errors):
            return
        
        filled_forms = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                filled_forms += 1
        
        if filled_forms == 0:
            raise forms.ValidationError("Please fill out at least one product form.")

BulkProductFormSet = formset_factory(
    BulkProductForm, 
    formset=BaseBulkProductFormSet,
    extra=10,  # Start with 10 empty forms
    can_delete=True,
    max_num=50  # Allow up to 50 products at once
)
