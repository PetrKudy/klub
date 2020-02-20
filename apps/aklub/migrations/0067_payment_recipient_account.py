# Generated by Django 2.2.10 on 2020-02-20 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0066_auto_20200128_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='recipient_account',
            field=models.ForeignKey(help_text='Recipient bank account number', null=True, on_delete=django.db.models.deletion.SET_NULL, to='aklub.MoneyAccount', verbose_name='Recipient account'),
        ),
    ]
