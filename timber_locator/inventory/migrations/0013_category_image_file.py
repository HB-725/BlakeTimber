from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0012_rename_location_product_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image_file",
            field=models.FileField(blank=True, null=True, upload_to="category_images/", verbose_name="Image File"),
        ),
    ]
