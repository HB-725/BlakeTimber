from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0016_product_price_default"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
    ]
