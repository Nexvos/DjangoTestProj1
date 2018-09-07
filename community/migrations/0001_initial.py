# Generated by Django 2.0.3 on 2018-08-17 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityGroup',
            fields=[
                ('community_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('private', models.BooleanField(default=False)),
                ('daily_payout', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('total_number_users', models.IntegerField(default=0, editable=False)),
            ],
        ),
    ]
