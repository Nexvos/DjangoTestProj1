# Generated by Django 2.0.3 on 2018-06-15 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0011_auto_20180615_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='modified',
            field=models.DateTimeField(editable=False),
        ),
    ]