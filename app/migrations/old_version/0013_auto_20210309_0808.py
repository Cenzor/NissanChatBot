# Generated by Django 3.0.2 on 2021-03-09 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20210309_0801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer',
            name='phone',
            field=models.TextField(null=True),
        ),
    ]
