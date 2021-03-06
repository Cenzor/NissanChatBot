# Generated by Django 3.0.2 on 2021-05-09 10:49

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.TextField(verbose_name='Бренд')),
                ('name', models.TextField(verbose_name='Название')),
                ('model_group_id', models.IntegerField(verbose_name='Айди модельной группы')),
                ('model_code', models.TextField(verbose_name='Айди модели')),
                ('year', models.IntegerField(verbose_name='Год')),
                ('min_price', models.IntegerField(verbose_name='Минимальная цена')),
                ('disabled', models.BooleanField(default=False, verbose_name='Выключить')),
                ('versions', models.TextField(verbose_name='Версии')),
                ('photo', models.TextField(default=None, null=True, verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'авто',
                'verbose_name_plural': 'Авто',
            },
        ),
        migrations.CreateModel(
            name='CarData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('vin', models.TextField()),
                ('versions', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Dealer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('longitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('street', models.TextField()),
                ('zip', models.IntegerField()),
                ('city', models.TextField()),
                ('phone', models.TextField(null=True)),
                ('helios_code', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FaqList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(blank=True, default='', verbose_name='Вопрос')),
                ('answer', models.TextField(blank=True, default='', verbose_name='Ответ')),
                ('link', models.TextField(blank=True, default='', verbose_name='Ссылка')),
                ('keywords', models.TextField(blank=True, default='', verbose_name='Ключевые слова')),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
            },
        ),
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('longitude', models.DecimalField(decimal_places=5, max_digits=32)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('api_id', models.IntegerField(verbose_name='Айди API')),
            ],
            options={
                'verbose_name': 'услуги',
                'verbose_name_plural': 'Услуги',
            },
        ),
        migrations.CreateModel(
            name='SpecialCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('text', models.TextField(verbose_name='Контент')),
                ('is_disabled', models.BooleanField(default=False, verbose_name='Выключить отображение')),
            ],
            options={
                'verbose_name': 'спец. прогр.',
                'verbose_name_plural': 'Спец. программы',
            },
        ),
        migrations.CreateModel(
            name='VKAccount',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.TextField(verbose_name='Имя')),
                ('last_name', models.TextField(blank=True, default='', null=True, verbose_name='Фамилия')),
                ('username', models.TextField(blank=True, default=None, null=True, verbose_name='Логин')),
                ('dialog', models.TextField(default='start', verbose_name='Системный диалог')),
                ('vin', models.TextField(blank=True, default=None, null=True, verbose_name='VIN')),
                ('mailing', models.BooleanField(default=True, verbose_name='Подписка на рассылку')),
                ('temp', models.TextField(blank=True, default='', verbose_name='Временные данные')),
                ('parking', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Parking', verbose_name='Паркинг')),
            ],
            options={
                'verbose_name': 'вк аккаунт',
                'verbose_name_plural': 'ВК Аккаунты',
            },
        ),
        migrations.CreateModel(
            name='TGAccount',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.TextField(verbose_name='Имя')),
                ('last_name', models.TextField(blank=True, default='', null=True, verbose_name='Фамилия')),
                ('username', models.TextField(blank=True, default=None, null=True, verbose_name='Логин')),
                ('dialog', models.TextField(default='start', verbose_name='Системный диалог')),
                ('vin', models.TextField(blank=True, default=None, null=True, verbose_name='VIN')),
                ('mailing', models.BooleanField(default=True, verbose_name='Подписка на рассылку')),
                ('temp', models.TextField(blank=True, default='', verbose_name='Временные данные')),
                ('parking', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Parking', verbose_name='Паркинг')),
            ],
            options={
                'verbose_name': 'телеграм аккаунт',
                'verbose_name_plural': 'Телеграм Аккаунты',
            },
        ),
        migrations.CreateModel(
            name='TestDrive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата создания')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_drive_tickets', to='app.Car', verbose_name='Автомобиль')),
                ('dealer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_drive_tickets', to='app.Dealer', verbose_name='Дилер')),
                ('user_tg', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_drive_tickets', to='app.TGAccount', verbose_name='Telegram пользователь')),
            ],
            options={
                'verbose_name': 'тест-драйв',
                'verbose_name_plural': 'Заявки на тест-драйв',
            },
        ),
        migrations.CreateModel(
            name='SpecialItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('text', models.TextField(verbose_name='Контент')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.SpecialCategory', verbose_name='Спец. программа')),
            ],
            options={
                'verbose_name': 'элемент спец. программы',
                'verbose_name_plural': 'Элементы спец. программ',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('type', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('user_tg', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback', to='app.TGAccount')),
            ],
        ),
        migrations.CreateModel(
            name='FBAccount',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.TextField(verbose_name='Имя')),
                ('last_name', models.TextField(blank=True, default='', null=True, verbose_name='Фамилия')),
                ('username', models.TextField(blank=True, default=None, null=True, verbose_name='Логин')),
                ('dialog', models.TextField(default='start', verbose_name='Системный диалог')),
                ('vin', models.TextField(blank=True, default=None, null=True, verbose_name='VIN')),
                ('mailing', models.BooleanField(default=True, verbose_name='Подписка на рассылку')),
                ('temp', models.TextField(blank=True, default='', verbose_name='Временные данные')),
                ('parking', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Parking', verbose_name='Паркинг')),
            ],
            options={
                'verbose_name': 'фб аккаунт',
                'verbose_name_plural': 'ФБ Аккаунты',
            },
        ),
    ]
