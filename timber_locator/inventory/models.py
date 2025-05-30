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
        # Extract numbers from name (e.g., "90 x 35 mm" -> (90, 35))
        try:
            parts = self.name.split('x')
            width = int(parts[0].strip())
            height = int(parts[1].strip().split()[0])
            return (width, height)
        except (ValueError, IndexError):
            return (0, 0)  # Default for invalid formats

    class Meta:
        ordering = ['name']  # This will be overridden by the natural sorting in the view

class Product(models.Model):
    profile   = models.ForeignKey(Profile, on_delete=models.CASCADE)
    length    = models.DecimalField(max_digits=4, decimal_places=1, help_text="Length in meters")
    in_number = models.CharField("I/N Number", max_length=50, unique=True)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    location  = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField("Image URL", max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.profile.name} – {self.length} m"

    def barcode_svg(self):
        # Using TEC-IT barcode service
        barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={self.in_number}&code=Code128&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&bgcolor=%23ffffff&qunit=Mm&quiet=0"
        return mark_safe(f'<img src="{barcode_url}" alt="Barcode" style="width: 100%; height: auto;">')

    class Meta:
        ordering = ['length']  # Sort products by length ascending
