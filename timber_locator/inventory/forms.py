from django import forms
from django.forms import formset_factory, BaseFormSet
from .models import Category, Profile, Product

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
    price = forms.DecimalField(
        max_digits=8, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': '0.01', 
            'placeholder': '0.00',
            'style': 'width: 120px;'
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
