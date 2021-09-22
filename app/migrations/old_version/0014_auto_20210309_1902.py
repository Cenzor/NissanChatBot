# Generated by Django 3.0.2 on 2021-03-09 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20210309_0808'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('longitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='tgaccount',
            name='parking',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Parking'),
        ),
    ]
