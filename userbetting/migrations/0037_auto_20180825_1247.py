# Generated by Django 2.0.3 on 2018-08-25 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0036_auto_20180821_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='groups',
            field=models.ManyToManyField(related_name='group_tournaments', to='community.CommunityGroup'),
        ),
    ]
