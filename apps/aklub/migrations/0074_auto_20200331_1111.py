# Generated by Django 2.2.10 on 2020-04-01 11:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0073_auto_20200206_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativeunit',
            name='slug',
            field=models.SlugField(blank=True, default=None, help_text='Identifier of the administrative_unit', max_length=100, null=True, unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='send_to_users',
            field=models.ManyToManyField(blank=True, help_text='All users who should receive the communication', to=settings.AUTH_USER_MODEL, verbose_name='send to users'),
        ),

    ]