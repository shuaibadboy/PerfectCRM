# Generated by Django 2.1.3 on 2019-06-26 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20190621_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='order_by',
            field=models.SmallIntegerField(null=True, verbose_name='排序'),
        ),
    ]
