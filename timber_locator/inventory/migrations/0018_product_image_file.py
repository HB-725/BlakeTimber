from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0017_remove_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_file",
            field=models.FileField(blank=True, null=True, upload_to="product_images/", verbose_name="Image File"),
        ),
    ]
