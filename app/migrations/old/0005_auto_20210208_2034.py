# Generated by Django 3.0.2 on 2021-02-08 20:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210117_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tgaccount',
            name='dialog',
        ),
        migrations.RemoveField(
            model_name='tgaccount',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='tgaccount',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='tgaccount',
            name='temp',
        ),
        migrations.RemoveField(
            model_name='tgaccount',
            name='username',
        ),
        migrations.RemoveField(
            model_name='tgaccount',
            name='vin',
        ),
        migrations.DeleteModel(
            name='VKAccount',
        ),
    ]
