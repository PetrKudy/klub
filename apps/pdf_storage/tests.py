from aklub.models import UserProfile

from api.tests import user_login_mixin

from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from freezegun import freeze_time

from model_mommy import mommy


class RelatedPdfListViewViewTest(TestCase):
    def setUp(self):
        user_login_mixin()
        user = mommy.make("aklub.UserProfile", first_name='author', last_name='author_last')
        unit = mommy.make("aklub.AdministrativeUnit")
        self.pdf = mommy.make(
            'pdf_storage.PdfStorage',
            name='test_pdf',
            topic="test_topic",
            related_ids=[1, 2, 3],
            author=user,
            pdf_file=File(open("apps/aklub/test_data/empty_pdf.pdf", "rb")),
            administrative_unit=unit,
        )
        # unrelated pdf
        mommy.make(
            'pdf_storage.PdfStorage',
            name='test_pdf',
            topic="test_topic",
            related_ids=[2, 3],
            author=user,
            pdf_file=File(open("apps/aklub/test_data/empty_pdf.pdf", "rb")),
            administrative_unit=unit,
        )

    def test_get_request(self):
        url = reverse('pdfstorage_list', kwargs={'related_id': '1'})
        header = {'Authorization': 'Bearer foo'}
        # required fields

        response = self.client.get(url, **header)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 1)
        obj = data[0]
        self.assertEqual(obj['id'], self.pdf.id)
        self.assertEqual(obj['name'], self.pdf.name)
        self.assertEqual(obj['topic'], self.pdf.topic)
        self.assertEqual(obj['author'], self.pdf.author.person_name())
        self.assertEqual(parse_datetime(obj['created']), parse_datetime(str(self.pdf.created)))


class PaidPdfDownloadViewTest(TestCase):
    def setUp(self):
        user_login_mixin()
        user = UserProfile.objects.get(username='user_can_access')
        unit = mommy.make("aklub.AdministrativeUnit", name='test_unit')
        event = mommy.make(
            "aklub.event",
            name='event_test',
            administrative_units=[unit, ],
        )
        self.api_acc = mommy.make(
            "aklub.ApiAccount",
            event=event,
            administrative_unit=unit,
        )
        self.dpch = mommy.make(
            "aklub.DonorPaymentChannel",
            money_account=self.api_acc,
            event=event,
            user=user,
        )
        self.pdf = mommy.make(
            'pdf_storage.PdfStorage',
            name='test_pdf',
            topic="test_topic",
            related_ids=[1, 2, 3],
            author=user,
            pdf_file=File(open("apps/aklub/test_data/empty_pdf.pdf", "rb")),
            administrative_unit=unit,
        )

    @freeze_time("2015-5-1")
    def test_get_request(self):
        last_payment_date = "2015-4-25"
        mommy.make(
            "aklub.payment",
            date=last_payment_date,
            amount=200,
            recipient_account=self.api_acc,
            user_donor_payment_channel=self.dpch,
        )
        url = reverse('pdfstorage_detail', kwargs={'id': self.pdf.id})
        header = {'Authorization': 'Bearer foo'}
        # required fields
        response = self.client.get(url, **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.pdf.pdf_file.url, response.json()['download_url'])

    @freeze_time("2015-5-1")
    def test_get_request_fail(self):
        last_payment_date = "2015-3-5"
        mommy.make(
            "aklub.payment",
            date=last_payment_date,
            amount=200,
            recipient_account=self.api_acc,
            user_donor_payment_channel=self.dpch,
        )
        url = reverse('pdfstorage_detail', kwargs={'id': self.pdf.id})
        header = {'Authorization': 'Bearer foo'}
        # required fields
        response = self.client.get(url, **header)
        self.assertEqual(response.status_code, 404)


class AllRelatedIdsViewTest(TestCase):
    def setUp(self):
        user_login_mixin()
        unit = mommy.make("aklub.AdministrativeUnit", name='test_unit')
        self.pdf_1 = mommy.make(
            'pdf_storage.PdfStorage',
            name='test_pdf',
            topic="test_topic",
            related_ids=[1, 2, 3],
            pdf_file=File(open("apps/aklub/test_data/empty_pdf.pdf", "rb")),
            administrative_unit=unit,
            )
        self.pdf_2 = mommy.make(
            'pdf_storage.PdfStorage',
            name='test_pdf',
            topic="test_topic",
            related_ids=[3, 2, 99, 110],
            pdf_file=File(open("apps/aklub/test_data/empty_pdf.pdf", "rb")),
            administrative_unit=unit,
            )

    def test_get_all_related_ids(self):
        url = reverse('pdf_storage_all_related_ids')
        header = {'Authorization': 'Bearer foo'}
        response = self.client.get(url, **header)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(response.json()['ids']), sorted(set(self.pdf_1.related_ids + self.pdf_2.related_ids)))
