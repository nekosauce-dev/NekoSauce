# Generated by Django 4.2.5 on 2023-10-04 23:19

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sauces", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="sauce",
            index=django.contrib.postgres.indexes.BTreeIndex(
                models.F("source_id"),
                models.F("source_site_id"),
                name="sauces__source_site_id__idx",
            ),
        ),
    ]