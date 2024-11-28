# Generated by Django 3.2.3 on 2024-11-27 19:33

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default=core.utils.generate_short_link, max_length=6, verbose_name='Короткая ссылка'),
        ),
    ]
