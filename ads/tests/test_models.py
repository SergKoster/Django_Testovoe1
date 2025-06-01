from django.test import TestCase
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal

class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='pass')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Desc',
            category='Books',
            condition='New'
        )

    def test_ad_str(self):
        self.assertEqual(str(self.ad), 'Test Ad (alice)')

    def test_created_at_auto(self):
        self.assertIsNotNone(self.ad.created_at)

class ExchangeProposalModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('bob', password='pass')
        self.user2 = User.objects.create_user('carol', password='pass')
        self.ad1 = Ad.objects.create(user=self.user1, title='A1', description='', category='X', condition='Y')
        self.ad2 = Ad.objects.create(user=self.user2, title='A2', description='', category='X', condition='Y')
        self.prop = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Offer!'
        )

    def test_default_status(self):
        self.assertEqual(self.prop.status, 'pending')

    def test_str(self):
        display = self.prop.get_status_display()
        expected = f"Proposal from Ad {self.ad1.id} to Ad {self.ad2.id} ({display})"
        self.assertEqual(str(self.prop), expected)
