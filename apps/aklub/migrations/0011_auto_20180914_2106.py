# Generated by Django 2.0.1 on 2018-09-14 21:06

import aklub.autocom
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0010_auto_20180822_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='email_confirmation_redirect',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='subject',
            field=models.CharField(help_text='Same variables as in template can be used', max_length=130, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='subject_en',
            field=models.CharField(blank=True, help_text='English version of the subject. If empty, English speaking users will not receive this communication.<br/>Same variables as in template can be used', max_length=130, null=True, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='English subject'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='template',
            field=models.TextField(help_text='Template can contain following variable substitutions: <br/>{mr|mrs} or {mr/mrs}, $addressment, $name, $firstname, $surname, $street, $city, $zipcode, $email, $telephone, $regular_amount, $regular_frequency, $var_symbol, $last_payment_amount, $auth_token', max_length=50000, null=True, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='template_en',
            field=models.TextField(blank=True, help_text='Same variables as in template can be used', max_length=50000, null=True, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='English template'),
        ),
    ]