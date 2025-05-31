from django.db import models
from django.utils.html import mark_safe

# Create your models here.
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name   = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(max_length=100, unique=True)
    image_url = models.URLField("Image URL", max_length=500, blank=True, null=True)

    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name
    

# inventory/models.py (continued)
class Profile(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name     = models.CharField(max_length=50)  # e.g. "90 x 35 mm"
    image_url = models.URLField("Image URL", max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def get_dimensions(self):
        # Extract numbers from name 
        # Handles: "90 x 35mm" (timber) -> (90, 35) 
        # Handles: "2400 x 1200 x 10mm" (plasterboard) -> (2400, 1200, 10)
        # Handles: "3000 x 1350mm 10mm" (plasterboard variant) -> (3000, 1350, 10)
        try:
            # First, clean up the name and standardize the format
            cleaned_name = self.name.strip()
            
            # Handle different spacing patterns around 'mm'
            # "3000 x 1350mm 10mm" -> "3000 x 1350 x 10mm"
            # "3600 x 1200mm 10mm" -> "3600 x 1200 x 10mm"
            import re
            # Replace "mm " with " x " to standardize format
            cleaned_name = re.sub(r'mm\s+', ' x ', cleaned_name)
            
            parts = cleaned_name.split('x')
            dimensions = []
            
            for i, part in enumerate(parts):
                part = part.strip()
                # Remove 'mm' from the end if present
                if part.endswith('mm'):
                    part = part[:-2]
                elif ' ' in part:
                    part = part.split()[0]
                dimensions.append(int(part))
            
            # Return tuple based on number of dimensions
            if len(dimensions) == 2:
                return (dimensions[0], dimensions[1])  # timber: (width, height)
            elif len(dimensions) == 3:
                return (dimensions[0], dimensions[1], dimensions[2])  # plasterboard: (length, width, thickness)
            else:
                return (0, 0)  # Default for invalid formats
        except (ValueError, IndexError):
            return (0, 0)  # Default for invalid formats

    def get_width(self):
        """Get the width value for sorting purposes (first dimension for timber)"""
        dimensions = self.get_dimensions()
        return dimensions[0] if len(dimensions) >= 1 else 0
    
    def get_length(self):
        """Get the length value for sorting purposes (first dimension for plasterboard)"""
        dimensions = self.get_dimensions()
        length = 0
        if len(dimensions) == 3:  # plasterboard format: length x width x thickness
            length = dimensions[0]
        elif len(dimensions) == 2:  # timber format: width x height
            length = dimensions[0]
        
        return length
    
    def get_thickness(self):
        """Get the thickness value for sorting purposes (third dimension for MDF/sheets)"""
        dimensions = self.get_dimensions()
        thickness = 0
        if len(dimensions) == 3:  # MDF format: length x width x thickness
            thickness = dimensions[2]
        
        return thickness

    def get_display_image(self):
        """Return profile image URL with category fallback"""
        if self.image_url:
            return self.image_url
        elif self.category and self.category.image_url:
            return self.category.image_url
        else:
            return None

    class Meta:
        ordering = ['name']  # Default ordering - will be overridden in views with custom sorting

class Product(models.Model):
    # Products can be linked either to a Category directly OR through a Profile
    category  = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    profile   = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    option    = models.CharField(max_length=100, help_text="Product option (length, size, or other specifications)")
    in_number = models.CharField("I/N Number", max_length=50, unique=True)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    location  = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField("Image URL", max_length=500, blank=True, null=True)

    def clean(self):
        """Ensure either category or profile is set, but not both"""
        from django.core.exceptions import ValidationError
        if not self.category and not self.profile:
            raise ValidationError("Either category or profile must be set.")
        if self.category and self.profile:
            raise ValidationError("Cannot set both category and profile. Choose one.")

    def get_category(self):
        """Get the category, either direct or through profile"""
        if self.category:
            return self.category
        elif self.profile:
            return self.profile.category
        return None

    def get_name(self):
        """Get the product name from profile or category"""
        if self.profile:
            return self.profile.name
        elif self.category:
            return self.category.name
        return "Unnamed Product"

    def __str__(self):
        name = self.get_name()
        if self.option:
            return f"{name} – {self.option}"
        else:
            return name

    def get_dimension_display(self):
        """Return the option for display"""
        return self.option if self.option else ""

    def get_display_image(self):
        """Return image URL with fallback hierarchy: Product -> Profile -> Category"""
        if self.image_url:
            return self.image_url
        elif self.profile and self.profile.image_url:
            return self.profile.image_url
        elif self.profile and self.profile.category and self.profile.category.image_url:
            return self.profile.category.image_url
        elif self.category and self.category.image_url:
            return self.category.image_url
        else:
            return None

    def barcode_svg(self):
        # Using TEC-IT barcode service
        barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={self.in_number}&code=Code128&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&bgcolor=%23ffffff&qunit=Mm&quiet=0"
        return mark_safe(f'<img src="{barcode_url}" alt="Barcode" style="width: 100%; height: auto;">')

    class Meta:
        ordering = ['option']  # Sort products by option field
