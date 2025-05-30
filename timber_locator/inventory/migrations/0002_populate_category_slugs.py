from django.db import migrations
from django.utils.text import slugify

def populate_category_slugs(apps, schema_editor):
    Category = apps.get_model('inventory', 'Category')
    for category in Category.objects.all():
        if not category.slug:
            category.slug = slugify(category.name)
            category.save()

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_category_slugs),
    ] 