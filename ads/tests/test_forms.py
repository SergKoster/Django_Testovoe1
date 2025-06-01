from django.test import TestCase
from django.contrib.auth.models import User
from ads.models import Ad
from ads.forms import AdForm, ExchangeProposalForm

class AdFormTest(TestCase):
    def test_valid_data(self):
        user = User.objects.create_user('dave', password='pass')
        data = {
            'title': 'T', 'description': 'D',
            'category': 'C', 'condition': 'Cond'
        }
        form = AdForm(data)
        self.assertTrue(form.is_valid())
        ad = form.save(commit=False)
        self.assertEqual(ad.title, 'T')

    def test_missing_title(self):
        form = AdForm({'description': 'D', 'category':'C','condition':'X'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

class ExchangeProposalFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('eve', password='p')
        self.ad = Ad.objects.create(user=self.user, title='A', description='', category='C', condition='X')

    def test_ad_sender_queryset(self):
        form = ExchangeProposalForm(user=self.user)
        # поле ad_sender должно содержать только объявления self.user
        self.assertQuerySetEqual(form.fields['ad_sender'].queryset, [self.ad], lambda x: x)

    def test_without_user(self):
        # если не передать user, queryset пустой
        form = ExchangeProposalForm()
        self.assertFalse(form.fields['ad_sender'].queryset.exists())
