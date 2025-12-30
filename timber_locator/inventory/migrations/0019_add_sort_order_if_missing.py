from django.db import migrations


def add_sort_order_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()

    def column_names(table_name):
        return {col.name for col in connection.introspection.get_table_description(cursor, table_name)}

    for model_name in ("Category", "Profile", "Product"):
        model = apps.get_model("inventory", model_name)
        table = model._meta.db_table
        if "sort_order" in column_names(table):
            continue
        field = model._meta.get_field("sort_order")
        schema_editor.add_field(model, field)


def remove_sort_order(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()

    def column_names(table_name):
        return {col.name for col in connection.introspection.get_table_description(cursor, table_name)}

    for model_name in ("Category", "Profile", "Product"):
        model = apps.get_model("inventory", model_name)
        table = model._meta.db_table
        if "sort_order" not in column_names(table):
            continue
        field = model._meta.get_field("sort_order")
        schema_editor.remove_field(model, field)


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0018_product_image_file"),
    ]

    operations = [
        migrations.RunPython(add_sort_order_if_missing, reverse_code=remove_sort_order),
    ]
