from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0015_profile_image_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
    ]
