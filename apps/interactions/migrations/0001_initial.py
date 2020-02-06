# Generated by Django 2.2.9 on 2020-01-31 12:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aklub', '0066_auto_20200128_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=130)),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name of result')),
                ('sort', models.CharField(choices=[('promise', 'Promise'), ('ongoing', 'Ongoing communication'), ('dont_contact', "Don't contact again")], default='individual', max_length=30, verbose_name='Sort of result')),
            ],
        ),
        migrations.CreateModel(
            name='PetitionSignature',
            fields=[
                ('email_confirmed', models.BooleanField(default=False, verbose_name='Is confirmed via e-mail')),
                ('gdpr_consent', models.BooleanField(default=False, verbose_name='GDPR consent')),
                ('public', models.BooleanField(default=False, verbose_name='Publish my name in the list of supporters/petitents of this campaign')),
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of last change')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aklub.Event', verbose_name='Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InteractionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=130)),
                ('slug', models.SlugField(blank=True, help_text='Identifier of the Interaction Type', max_length=100, null=True, verbose_name='Slug')),
                ('event_bool', models.BooleanField(default=False, help_text='choose if event is visible in specific type of interaction ')),
                ('created_bool', models.BooleanField(default=False, help_text='choose if created is visible in specific type of interaction ')),
                ('updated_bool', models.BooleanField(default=False, help_text='choose if updated is visible in specific type of interaction ')),
                ('date_from_bool', models.BooleanField(default=False, help_text='choose if date_from is visible in specific type of interaction ')),
                ('date_to_bool', models.BooleanField(default=False, help_text='choose if date_to is visible in specific type of interaction ')),
                ('settlement_bool', models.BooleanField(default=False, help_text='choose if settlement is visible in specific type of interaction ')),
                ('note_bool', models.BooleanField(default=False, help_text='choose if note is visible in specific type of interaction ')),
                ('text_bool', models.BooleanField(default=False, help_text='choose if text is visible in specific type of interaction ')),
                ('attachment_bool', models.BooleanField(default=False, help_text='choose if attachment is visible in specific type of interaction ')),
                ('subject_bool', models.BooleanField(default=False, help_text='choose if subject is visible in specific type of interaction ')),
                ('summary_bool', models.BooleanField(default=False, help_text='choose if summary is visible in specific type of interaction ')),
                ('status_bool', models.BooleanField(default=False, help_text='choose if status is visible in specific type of interaction ')),
                ('result_bool', models.BooleanField(default=False, help_text='choose if result is visible in specific type of interaction ')),
                ('rating_bool', models.BooleanField(default=False, help_text='choose if rating is visible in specific type of interaction ')),
                ('next_step_bool', models.BooleanField(default=False, help_text='choose if next_step is visible in specific type of interaction ')),
                ('next_communication_date_bool', models.BooleanField(default=False, help_text='choose if next_communication_date is visible in specific type of interaction ')),
                ('created_by_bool', models.BooleanField(default=False, help_text='choose if created_by is visible in specific type of interaction ')),
                ('handled_by_bool', models.BooleanField(default=False, help_text='choose if handled_by is visible in specific type of interaction ')),
                ('send_bool', models.BooleanField(default=False, help_text='choose if send is visible in specific type of interaction ')),
                ('communication_type_bool', models.BooleanField(default=False, help_text='choose if communication_type is visible in specific type of interaction ')),
                ('dispatched_bool', models.BooleanField(default=False, help_text='choose if dispatched is visible in specific type of interaction ')),
                ('category', models.ForeignKey(help_text='Timeline display category', on_delete=django.db.models.deletion.CASCADE, to='interactions.InteractionCategory')),
            ],
        ),
        migrations.CreateModel(
            name='Interaction2',
            fields=[
                ('date_from', models.DateTimeField(blank=True, null=True, verbose_name='Date and time of the communication')),
                ('date_to', models.DateTimeField(blank=True, null=True, verbose_name='Date of creation')),
                ('settlement', models.CharField(blank=True, choices=[('a', 'Automatic'), ('m', 'Manual')], help_text='Handled by automatic or manual communication', max_length=30, null=True, verbose_name='Settlements')),
                ('note', models.TextField(blank=True, help_text='Internal notes about this communication', max_length=3000, null=True, verbose_name='Notes')),
                ('text', models.TextField(blank=True, help_text='Internal notes about this communication', max_length=3000, null=True, verbose_name='Notes')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='communication-attachments', verbose_name='Attachment')),
                ('subject', models.CharField(blank=True, help_text='The topic of this communication', max_length=130, null=True, verbose_name='Subject')),
                ('summary', models.TextField(blank=True, help_text='Text or summary of this communication', max_length=50000, null=True, verbose_name='Text')),
                ('status', models.CharField(blank=True, help_text='The topic of this communication', max_length=130, null=True, verbose_name='Subject')),
                ('rating', models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], help_text='Rate communication (school grades)', max_length=30, null=True, verbose_name='rating communication')),
                ('next_step', models.TextField(blank=True, help_text='What happens next', max_length=3000, null=True, verbose_name='Next steps')),
                ('next_communication_date', models.DateTimeField(blank=True, null=True, verbose_name='Date of creation')),
                ('send', models.BooleanField(blank=True, default=False, help_text='Request sending or resolving this communication. For emails, this means that the email will be immediatelly sent to the user. In other types of communications, someone must handle this manually.', null=True, verbose_name='Send / Handle')),
                ('communication_type', models.CharField(blank=True, choices=[('mass', 'Mass'), ('auto', 'Automatic'), ('individual', 'Individual')], default='individual', max_length=30, null=True, verbose_name='Type of communication')),
                ('dispatched', models.BooleanField(blank=True, default=False, help_text='Was this message already sent, communicated and/or resolved?', null=True, verbose_name='Dispatched / Done')),
                ('administrative_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aklub.AdministrativeUnit', verbose_name='administrative units')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by_communications', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('handled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_by_communications', to=settings.AUTH_USER_MODEL, verbose_name='Last handled by')),
                ('result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='interactions.Results', verbose_name='Result of communication')),
                ('type', models.ForeignKey(help_text='Type of interaction', on_delete=django.db.models.deletion.CASCADE, to='interactions.InteractionType')),
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of last change')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aklub.Event', verbose_name='Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
