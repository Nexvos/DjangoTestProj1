# Generated by Django 2.0.3 on 2018-07-16 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userbetting', '0027_tournament_api_series_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('stage_id', models.AutoField(primary_key=True, serialize=False)),
                ('api_series_id', models.IntegerField(blank=True, null=True)),
                ('api_tournament_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('api_modified_at', models.DateTimeField(blank=True, null=True, verbose_name='api_modified_at')),
                ('stage_name', models.CharField(max_length=120)),
                ('stage_start_date', models.DateTimeField(verbose_name='Tournament start date')),
                ('stage_end_date', models.DateTimeField(verbose_name='Tournament end date')),
                ('status', models.CharField(choices=[('Not begun', 'Not begun'), ('Ongoing', 'Ongoing'), ('Finished', 'Finished')], default='Not begun', max_length=30)),
            ],
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='api_tournament_id',
        ),
    ]
