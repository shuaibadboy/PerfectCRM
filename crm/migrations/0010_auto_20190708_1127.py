# Generated by Django 2.1.3 on 2019-07-08 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_auto_20190708_1121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('table_objs', '查看客户库表单权限'),)},
        ),
    ]