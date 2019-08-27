# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2017 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import pathlib
from datetime import datetime

from django.contrib import admin as django_admin, auth
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from django_admin_smoke_tests import tests

from freezegun import freeze_time

from model_mommy import mommy

from .recipes import donor_payment_channel_recipe, generic_profile_recipe, user_profile_recipe
from .utils import RunCommitHooksMixin
from .utils import print_response  # noqa
from .. import admin
from .. models import (
    AccountStatements, AutomaticCommunication, CompanyProfile, DonorPaymentChannel, Event,
    Interaction, MassCommunication, Profile, TaxConfirmation, UserProfile, UserYearPayments,
)


class CreateSuperUserMixin:

    def setUp(self):
        self.superuser = auth.get_user_model().objects.create_superuser(
            username='testuser',
            email='testuser@example.com',
            password='foo',
            polymorphic_ctype_id=ContentType.objects.get(model=UserProfile._meta.model_name).id,
        )


class AdminSmokeTest(CreateSuperUserMixin, tests.AdminSiteSmokeTest):
    fixtures = ['conditions', 'users']
    exclude_apps = ['helpdesk', 'postoffice', 'advanced_filters', 'celery_monitor']

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

        if not self.modeladmins:
            self.modeladmins = admin.site._registry.items()

        try:
            admin.autodiscover()
        except Exception:
            pass

    def post_request(self, post_data={}, params=None):
        request = self.factory.post(path='/', data=post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request


@override_settings(
    CELERY_ALWAYS_EAGER=True,
)
class AdminTest(CreateSuperUserMixin, RunCommitHooksMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def get_request(self, params=None):
        request = self.factory.get('/', params)

        request.user = self.superuser
        return request

    def post_request(self, post_data={}, params=None):
        request = self.factory.post('/', data=post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request

    def test_send_mass_communication(self):
        donor_payment_channel_recipe.make(id=3)
        donor_payment_channel_recipe.make(id=4)
        donor_payment_channel_recipe.make(id=2978)
        donor_payment_channel_recipe.make(id=2979)
        model_admin = django_admin.site._registry[DonorPaymentChannel]
        request = self.post_request({})
        queryset = DonorPaymentChannel.objects.all()
        response = admin.send_mass_communication_action(model_admin, request, queryset)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/aklub/masscommunication/add/?send_to_users=3%2C4%2C2978%2C2979")

    def test_send_mass_communication_userprofile(self):
        """
        Test, that sending mass communication works for ProfileAdmin.
        Communication shoul be send only once for every userprofile.
        """
        mutual_userprofile = mommy.make("aklub.UserProfile")
        foo = mommy.make("aklub.UserProfile")
        bar = mommy.make("aklub.UserProfile")
        donor_payment_channel_recipe.make(id=3, user=mutual_userprofile)
        donor_payment_channel_recipe.make(id=4, user=mutual_userprofile)
        donor_payment_channel_recipe.make(id=2978, user=foo)
        donor_payment_channel_recipe.make(id=2979, user=bar)
        model_admin = django_admin.site._registry[DonorPaymentChannel]
        request = self.post_request({})
        queryset = UserProfile.objects.exclude(username=self.superuser.username)
        response = admin.send_mass_communication_distinct_action(model_admin, request, queryset)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/aklub/masscommunication/add/?send_to_users=3%2C2978%2C2979")

    @freeze_time("2017-5-1")
    def test_tax_confirmation_generate(self):
        _foo_user = user_profile_recipe.make(id=2978, first_name="Foo")
        _foo_user.save()
        _bar_user = user_profile_recipe.make(id=2979, first_name="Bar")
        _bar_user.save()
        foo_user = donor_payment_channel_recipe.make(user=_foo_user)
        bar_user = donor_payment_channel_recipe.make(user=_bar_user)
        mommy.make("aklub.Payment", amount=350, date="2016-01-02", user_donor_payment_channel=foo_user, type="cash")
        mommy.make("aklub.Payment", amount=130, date="2016-01-02", user_donor_payment_channel=bar_user, type="cash")
        model_admin = django_admin.site._registry[TaxConfirmation]
        request = self.post_request({})
        response = model_admin.generate(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/aklub/taxconfirmation/")
        self.assertEqual(TaxConfirmation.objects.get(user_profile__id=2978, year=2016).amount, 350)
        confirmation_values = TaxConfirmation.objects.filter(year=2016).values('user_profile', 'amount', 'year').order_by('user_profile')
        expected_confirmation_values = [
            {'year': 2016, 'user_profile': 2978, 'amount': 350},
            {'year': 2016, 'user_profile': 2979, 'amount': 130},
        ]
        self.assertListEqual(list(confirmation_values), expected_confirmation_values)

    def test_useryearpayments(self):
        """
        Test, that the resulting amount in selected period matches
        """
        donor_payment_channel_recipe.make(
            payment_set=[
                mommy.make("aklub.Payment", date="2016-2-9", amount=150),
                mommy.make("aklub.Payment", date="2016-1-9", amount=100),
                mommy.make("aklub.Payment", date="2012-1-9", amount=100),
                mommy.make("aklub.Payment", date="2016-12-9", amount=100),  # Payment outside of selected period
            ],
        )
        model_admin = django_admin.site._registry[UserYearPayments]
        request = self.get_request({
            "drf__payment__date__gte": "01.07.2010",
            "drf__payment__date__lte": "10.10.2016",
        })
        response = model_admin.changelist_view(request)
        self.assertContains(response, '<td class="field-payment_total_by_year">350</td>', html=True)

    @freeze_time("2015-5-1")
    def test_account_statement_changelist_post(self):
        mommy.make("aklub.Event", darujme_name="Klub přátel Auto*Matu")
        mommy.make("aklub.Payment", SS=22258, type="darujme", operation_id="13954", date="2016-02-09")
        donor_payment_channel_recipe.make(id=2979, userprofile__email="bar@email.com", userprofile__language="cs")
        model_admin = django_admin.site._registry[AccountStatements]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        with open("apps/aklub/test_data/test_darujme.xls", "rb") as f:
            post_data = {
                '_save': 'Save',
                "type": "darujme",
                "date_from": "2010-10-01",
                "csv_file": f,
                'payment_set-TOTAL_FORMS': 0,
                'payment_set-INITIAL_FORMS': 0,
            }
            request = self.post_request(post_data=post_data)
            response = model_admin.add_view(request)
            self.run_commit_hooks()
            self.assertEqual(response.status_code, 302)
            obj = AccountStatements.objects.get(date_from="2010-10-01")
            self.assertEqual(response.url, "/aklub/accountstatements/")
            self.assertEqual(obj.payment_set.count(), 6)

            # self.assertEqual(request._messages._queued_messages[0].message, 'Skipped payments: Testing User 1 (test.user1@email.cz)')
            self.assertEqual(
                request._messages._queued_messages[0].message,
                'Položka typu Výpis z účtu "<a href="/aklub/accountstatements/%(id)s/change/">%(id)s (2015-05-01 00:00:00+00:00)</a>"'
                ' byla úspěšně přidána.' % {'id': obj.id},
            )

    @freeze_time("2015-5-1")
    def test_account_statement_changelist_post_bank_statement(self):
        donor_payment_channel_recipe.make(VS=120127010)
        model_admin = django_admin.site._registry[AccountStatements]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        with open("apps/aklub/test_data/Pohyby_5_2016.csv", "rb") as f:
            post_data = {
                '_save': 'Save',
                "type": "account",
                "csv_file": f,
                'payment_set-TOTAL_FORMS': 0,
                'payment_set-INITIAL_FORMS': 0,
            }
            request = self.post_request(post_data=post_data)
            response = model_admin.add_view(request)
            self.run_commit_hooks()
            self.assertEqual(response.status_code, 302)
            obj = AccountStatements.objects.get(date_from="2016-01-25")
            self.assertEqual(response.url, "/aklub/accountstatements/")
            self.assertEqual(obj.payment_set.count(), 4)

            # self.assertEqual(
            #     request._messages._queued_messages[0].message,
            #     'Payments without user: Testing user 1 (Bezhotovostní příjem), '
            #     'KRE DAN (KRE DAN), '
            #     'without variable symbol (without variable symbol)',
            # )
            self.assertEqual(
                request._messages._queued_messages[0].message,
                'Položka typu Výpis z účtu "<a href="/aklub/accountstatements/%(id)s/change/">%(id)s (2015-05-01 00:00:00+00:00)</a>"'
                ' byla úspěšně přidána.' % {'id': obj.id},
            )

    @override_settings(
        LANGUAGE_CODE='en',
    )
    def test_mass_communication_changelist_post_send_mails(self):
        mommy.make("Profile", id=2978, email="foo@email.com", language="cs")
        mommy.make("Profile", id=2979, email="bar@email.com", language="cs")
        mommy.make("Profile", id=3, email="baz@email.com", language="en")
        model_admin = django_admin.site._registry[MassCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'send_mails',
            'name': 'test communication',
            "method": "email",
            'date': "2010-03-03",
            "subject": "Subject",
            "send_to_users": [2978, 2979, 3],
            "template": "Test template",
        }
        request = self.post_request(post_data=post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = MassCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/aklub/masscommunication/%s/change/" % obj.id)
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "Communication sending was queued for 3 users",
        )
        edit_text = 'You may edit it again below.'
        self.assertEqual(
            request._messages._queued_messages[1].message,
            'The Mass Communication "<a href="/aklub/masscommunication/%s/change/">test communication</a>"'
            ' was added successfully. %s' % (obj.id, edit_text),
        )

    def test_mass_communication_changelist_post(self):
        model_admin = django_admin.site._registry[MassCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        attachment = SimpleUploadedFile("attachment.txt", b"attachment", content_type="text/plain")
        post_data = {
            '_continue': 'test_mail',
            'name': 'test communication',
            "method": "email",
            'date': "2010-03-03",
            "subject": "Subject",
            "attach_tax_confirmation": False,
            "attachment": attachment,
            "template": "Test template",
        }
        request = self.post_request(post_data=post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = MassCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/aklub/masscommunication/%s/change/" % obj.id)

    def test_automatic_communication_changelist_post(self):
        mommy.make("aklub.Condition", id=1)
        model_admin = django_admin.site._registry[AutomaticCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'test_mail',
            'name': 'test communication',
            'condition': 1,
            "method": "email",
            "subject": "Subject",
            "template": "Test template",
        }
        request = self.post_request(post_data=post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = AutomaticCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/aklub/automaticcommunication/%s/change/" % obj.id)

    def test_communication_changelist_post(self):
        user_profile = mommy.make('aklub.UserProfile')
        model_admin = django_admin.site._registry[Interaction]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_save': 'test_mail',
            "user": user_profile.id,
            "date_0": "2015-03-1",
            "date_1": "12:43",
            "method": "email",
            "subject": "Subject 123",
            "summary": "Test template",
        }
        request = self.post_request(post_data=post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = Interaction.objects.get()
        self.assertEqual(obj.subject, "Subject 123")
        self.assertEqual(obj.summary, "Test template")
        self.assertEqual(response.url, "/aklub/interaction/")

    def test_user_in_campaign_changelist_post(self):
        mommy.make("aklub.Event", id=1)
        mommy.make("aklub.Userprofile", id=2978)
        model_admin = django_admin.site._registry[DonorPaymentChannel]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'Save',
            'user': 2978,
            'VS': 1234,
            'activity_points': 13,
            'registered_support_0': "2010-03-03",
            'registered_support_1': "12:35",
            'regular_payments': 'promise',
            'campaign': '1',
            'verified': 1,
            'communications-TOTAL_FORMS': 1,
            'communications-INITIAL_FORMS': 0,
            'payment_set-TOTAL_FORMS': 0,
            'payment_set-INITIAL_FORMS': 0,
            "communications-0-method": "phonecall",
            "communications-0-subject": "Subject 1",
            "communications-0-summary": "Text 1",
            "communications-0-date_0": "2010-01-01",
            "communications-0-date_1": "11:11",
        }
        request = self.post_request(post_data=post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        donorpaymentchannel = DonorPaymentChannel.objects.get(VS=1234)
        self.assertEqual(response.url, "/aklub/donorpaymentchannel/%s/change/" % donorpaymentchannel.id)

        # self.assertEqual(donorpaymentchannel.activity_points, 13)
        # self.assertEqual(donorpaymentchannel.verified_by.username, 'testuser')

    def test_pair_variable_symbols(self):
        """ Test pair_variable_symbols action """
        payment_channel = donor_payment_channel_recipe.make(VS=123)
        payment = mommy.make("aklub.Payment", VS=123)
        account_statement = mommy.make(
            "aklub.AccountStatements",
            payment_set=[payment],
        )
        request = self.post_request()
        admin.pair_variable_symbols(None, request, [account_statement])
        payment.refresh_from_db()
        self.assertEqual(payment.user_donor_payment_channel, payment_channel)
        self.assertEqual('Variabilní symboly úspěšně spárovány.', request._messages._queued_messages[0].message)

    def test_profile_post(self):
        model_admin = django_admin.site._registry[Group]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        group_post_data = {
            'name': 'test',
            'permissions': 1,
        }
        request = self.post_request(post_data=group_post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 1)

        managementform_data = {
            'preference_set-TOTAL_FORMS': 0,
            'preference_set-INITIAL_FORMS': 0,
            'preference_set-MIN_NUM_FORMS': 0,
            'preference_set-MAX_NUM_FORMS': 0,
            'telephone_set-TOTAL_FORMS': 0,
            'telephone_set-INITIAL_FORMS': 0,
            'telephone_set-MIN_NUM_FORMS': 0,
            'telephone_set-MAX_NUM_FORMS': 1000,
            'userchannels-TOTAL_FORMS': 0,
            'userchannels-INITIAL_FORMS': 0,
            'userchannels-MIN_NUM_FORMS': 0,
            'userchannels-MAX_NUM_FORMS': 1000,
            'interaction_set-TOTAL_FORMS': 0,
            'interaction_set-INITIAL_FORMS': 0,
            'interaction_set-MIN_NUM_FORMS': 0,
            'interaction_set-MAX_NUM_FORMS': 1000,
        }

        actions = ['add_view', 'change_view']
        child_models = Profile.__subclasses__()

        for child_model in child_models:
            model_admin = django_admin.site._registry[child_model]
            request = self.get_request()
            response = model_admin.add_view(request)
            self.assertEqual(response.status_code, 200)

            for view_method_name in actions:
                action = view_method_name.split('_')[0]
                model_name = child_model._meta.model_name
                test_str = '{}.{}'.format(action, model_name)
                profile_post_data = {
                    'username': '{}'.format(test_str),
                    'email': '{0}@{0}.test'.format(test_str),
                    'language': 'cs',
                    'is_staff': 'on',
                    'groups': Group.objects.get().id,
                }

                if 'sex' in (f.name for f in child_model._meta.fields):
                    profile_post_data.update({'sex': 'male'})
                if 'crn' in (f.name for f in child_model._meta.fields):
                    profile_post_data.update({'crn': '00000000'})
                profile_post_data.update(managementform_data)

                view_method = getattr(model_admin, view_method_name)
                request = self.post_request(post_data=profile_post_data)

                if action == 'change':
                    user_id = str(Profile.objects.get(username='add.{}'.format(model_name)).id)
                    response = view_method(request, object_id=user_id)
                else:
                    response = view_method(request)

                self.assertEqual(response.status_code, 302)

                user = Profile.objects.get(username='{}'.format(test_str))
                group_id = user.groups.all().values_list("id", flat=True)[0]

                self.assertEqual(user.username, profile_post_data['username'])
                self.assertEqual(user.email, profile_post_data['email'])
                self.assertEqual(user.is_staff, True)
                self.assertEqual(group_id, profile_post_data['groups'])

        new_users = Profile.objects.exclude(username=self.superuser.username)
        self.assertEqual(new_users.count(), len(child_models))

        for user in new_users:
            model_admin = django_admin.site._registry[user._meta.model]
            delete_post_data = {
                'submit': 'Ano, jsem si jist(a)',
            }
            request = self.post_request(post_data=delete_post_data)
            response = model_admin.delete_view(request, object_id=str(user.id))
            self.assertEqual(response.status_code, 302)

        self.assertEqual(Profile.objects.exclude(username=self.superuser.username).count(), 0)


class AdminImportExportTests(CreateSuperUserMixin, TestCase):
    fixtures = ['conditions', 'users', 'communications']

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.client.force_login(self.superuser)

    def get_request(self, params=None):
        request = self.factory.get('/', params)

        request.user = self.superuser
        return request

    def post_request(self, post_data={}, params=None):
        request = self.factory.post('/', data=post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request

    def test_paymetnchannel_export(self):
        address = "/aklub/donorpaymentchannel/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(
            response,
            '2978,2,2978,,Test,User,,male,test.user@email.cz,,Praha 4,,120127010,0,regular,monthly,2015-12-16 17:22:30,1,cs,,,,100,',
            # TODO: check transforming following data into another models
            # ',Test,User,,male,,test.user@email.cz,,Praha 4,,120127010,0,1,regular,monthly,2015-12-16 17:22:30,'
            # '"Domníváte se, že má město po zprovoznění tunelu Blanka omezit tranzit historickým centrem? '
            # 'Ano, hned se zprovozněním tunelu",editor,1,cs,,,,0,0.0,100',
        )

    def test_profile_export(self):
        profiles_data = [
            {
                'type': 'user',
                'model_name': UserProfile._meta.model_name,
                'vs': '140147010',
                'extra_fields': {'sex': 'male'},
            },
            {
                'type': 'company',
                'model_name': CompanyProfile._meta.model_name,
                'vs': '150157010',
                'extra_fields': {'crn': '11223344'},
            },
        ]
        # event = mommy.make(
        #     'aklub.Event',
        #     name='Klub přátel Auto*Matu',
        #     created='2015-12-16',
        #     slug='klub',
        #     allow_statistics=True,
        #     darujme_api_id=38571205,
        #     darujme_project_id=38571205,
        #     acquisition_campaign=True,
        #     enable_signing_petitions=True,
        #     enable_registration=True,
        #     darujme_name='Klub přátel Auto*Matu',
        # )
        event = Event.objects.get(pk=2)
        for profile_type in profiles_data:
            model_name = profile_type['model_name']
            generic_profile_recipe._model = 'aklub.{}'.format(model_name)
            fields = {
                'username': 'test.{}'.format(model_name),
                'first_name': 'First_name_{}'.format(model_name),
                'last_name': 'Last_name_{}'.format(model_name),
                'email': 'test.{0}@{0}.test'.format(model_name),
            }
            fields.update(profile_type['extra_fields'])
            user = generic_profile_recipe.make(**fields)
            mommy.make(
                'aklub.Interaction',
                dispatched=False,
                date='2016-2-9',
                user=user,
            )
            mommy.make(
                'aklub.TaxConfirmation',
                user_profile=user,
                year=2014,
                amount=2014,
            )
            mommy.make(
                'aklub.DonorPaymentChannel',
                user=user,
                expected_date_of_first_payment=datetime.strptime('2015-12-16', '%Y-%m-%d'),
                no_upgrade=False,
                registered_support='2015-12-16T18:22:30.128',
                regular_amount=100,
                regular_frequency='monthly',
                regular_payments='regular',
                event=event,
                VS=profile_type['vs'],
            )

        address = '/aklub/profile/export/'
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        date_time_format = '%Y-%m-%d %H:%M:%S'
        user = Profile.objects.get(username='test.{}'.format(UserProfile._meta.model_name))
        self.assertContains(
            response,
            ''.join([
                ',test.userprofile@userprofile.test,,male,,',
                '"VS:140147010\nevent:Klub přátel Auto*Matu\nbank_accout:\nuser_bank_account:\n\n"',
                ',userprofile,,,,test.userprofile,First_name_userprofile,Last_name_userprofile,1,',
                '2016-09-16 16:22:30,,,,,,,en,,Praha 4,Česká republika,,1,,,Česká republika,,,1,,,0,',
                '0,,,{created},{updated},1,,,,0,0,0,0'.format(
                    created=user.created.strftime(date_time_format),
                    updated=user.updated.strftime(date_time_format),
                )]
            )
        )
        user = Profile.objects.get(username='test.{}'.format(CompanyProfile._meta.model_name))
        self.assertContains(
            response,
            ''.join([
                ',test.companyprofile@companyprofile.test,11223344,,,',
                '"VS:150157010\nevent:Klub přátel Auto*Matu\nbank_accout:\nuser_bank_account:\n\n"',
                ',companyprofile,,,,test.companyprofile,First_name_companyprofile,Last_name_companyprofile,',
                '1,2016-09-16 16:22:30,,,,,,,en,,Praha 4,Česká republika,,1,,,Česká republika,,,1,,,0,0,,,',
                '{created},{updated},1,,,,0,0,0,0'.format(
                    created=user.created.strftime(date_time_format),
                    updated=user.updated.strftime(date_time_format),
                )]
            )
        )

    def test_profile_import(self):
        p = pathlib.PurePath(__file__)
        csv_file = p.parents[1] / 'test_data' / 'create_profiles.csv'
        fp = open(csv_file)
        address = '/aklub/profile/import/'
        post_data = {
            'import_file': fp,
            'input_format': 0,
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'test.companyprofile@companyprofile.test',
            html=True,
        )
        self.assertContains(
            response,
            'test.userprofile@userprofile.test',
            html=True,
        )
        self.assertContains(
            response,
            'male',
            html=True,
        )
        self.assertContains(
            response,
            '11223344',
            html=True,
        )
        # TODO
        # https://stackoverflow.com/questions/57644863/how-could-i-write-test-wich-test-import-data-from-csv-file-into-db-model-via-dj
        # fp = open(csv_file)
        # post_data = {
        # }
        # address = '/aklub/profile/process_import/'
        # response = self.client.post(address, post_data, content_type='application/x-www-form-urlencoded')
