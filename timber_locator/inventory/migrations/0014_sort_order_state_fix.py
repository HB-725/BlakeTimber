from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0013_category_image_file"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="category",
                    name="sort_order",
                    field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
                ),
                migrations.AddField(
                    model_name="profile",
                    name="sort_order",
                    field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
                ),
                migrations.AddField(
                    model_name="product",
                    name="sort_order",
                    field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
                ),
            ],
            database_operations=[],
        ),
    ]
