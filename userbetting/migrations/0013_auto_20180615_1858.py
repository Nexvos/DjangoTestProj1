# Generated by Django 2.0.3 on 2018-06-15 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0012_auto_20180615_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='colour',
            field=models.CharField(default='#D3D3D3', max_length=7),
        ),
    ]