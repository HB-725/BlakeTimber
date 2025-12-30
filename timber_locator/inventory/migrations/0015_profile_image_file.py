from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0014_sort_order_state_fix"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="image_file",
            field=models.FileField(blank=True, null=True, upload_to="profile_images/", verbose_name="Image File"),
        ),
    ]
