# Generated by Django 2.0.3 on 2018-06-20 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0017_auto_20180620_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winning_team',
            field=models.CharField(blank=True, choices=[('Not Decided', 'Not Decided'), (None, None), (None, None)], default='Not Decided', max_length=60, null=True),
        ),
    ]