# Generated by Django 5.2.3 on 2025-06-28 21:33

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receta',
            name='receta',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
