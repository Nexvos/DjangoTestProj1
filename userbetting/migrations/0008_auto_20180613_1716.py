# Generated by Django 2.0.3 on 2018-06-13 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0007_auto_20180613_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='created',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='bet',
            name='modified',
            field=models.DateTimeField(),
        ),
    ]
