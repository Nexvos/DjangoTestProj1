# Generated by Django 2.0.3 on 2018-08-21 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('profiles', '0012_auto_20180817_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='community_invites_group', to='community.CommunityGroup')),
            ],
        ),
        migrations.AlterField(
            model_name='profile',
            name='groups',
            field=models.ManyToManyField(related_name='profiles_groups', through='profiles.Wallet', to='community.CommunityGroup'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='wallets_group', to='community.CommunityGroup'),
        ),
        migrations.AddField(
            model_name='communityinvite',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='community_invites_profile', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='groups_invited_to',
            field=models.ManyToManyField(related_name='profiles_invites', through='profiles.CommunityInvite', to='community.CommunityGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='communityinvite',
            unique_together={('profile', 'group')},
        ),
    ]