# Generated by Django 3.0.2 on 2021-04-12 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210330_2158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='car',
            options={'verbose_name': 'авто', 'verbose_name_plural': 'Авто'},
        ),
        migrations.AlterModelOptions(
            name='faqlist',
            options={'verbose_name': 'FAQ', 'verbose_name_plural': 'FAQ'},
        ),
        migrations.AlterModelOptions(
            name='tgaccount',
            options={'verbose_name': 'телеграм аккаунт', 'verbose_name_plural': 'Телеграм Аккаунты'},
        ),
        migrations.AlterField(
            model_name='car',
            name='brand',
            field=models.TextField(verbose_name='Бренд'),
        ),
        migrations.AlterField(
            model_name='car',
            name='disabled',
            field=models.BooleanField(default=False, verbose_name='Выключить'),
        ),
        migrations.AlterField(
            model_name='car',
            name='min_price',
            field=models.IntegerField(verbose_name='Минимальная цена'),
        ),
        migrations.AlterField(
            model_name='car',
            name='model_code',
            field=models.TextField(verbose_name='Айди модели'),
        ),
        migrations.AlterField(
            model_name='car',
            name='model_group_id',
            field=models.IntegerField(verbose_name='Айди модельной группы'),
        ),
        migrations.AlterField(
            model_name='car',
            name='name',
            field=models.TextField(verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='car',
            name='photo',
            field=models.TextField(default=None, null=True, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='car',
            name='versions',
            field=models.TextField(verbose_name='Версии'),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(verbose_name='Год'),
        ),
        migrations.AlterField(
            model_name='faqlist',
            name='answer',
            field=models.TextField(blank=True, default='', verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='faqlist',
            name='keywords',
            field=models.TextField(blank=True, default='', verbose_name='Ключевые слова'),
        ),
        migrations.AlterField(
            model_name='faqlist',
            name='link',
            field=models.TextField(blank=True, default='', verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='faqlist',
            name='question',
            field=models.TextField(blank=True, default='', verbose_name='Вопрос'),
        ),
    ]
