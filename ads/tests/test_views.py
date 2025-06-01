from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal


class AdViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='frank', password='pass')
        self.client.login(username='frank', password='pass')
        self.ad = Ad.objects.create(
            user=self.user,
            title='X',
            description='D',
            category='C',
            condition='Y'
        )

    def test_ad_list_view(self):
        url = reverse('ad_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'X')

    def test_create_ad_view(self):
        url = reverse('create_ad')
        data = {'title': 'New', 'description': 'Desc', 'category': 'C', 'condition': 'Y'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='New').exists())

    def test_delete_ad_view(self):
        url = reverse('delete_ad', args=[self.ad.id])
        # GET → confirmation page
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # POST → actually delete
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('ad_list'))
        self.assertFalse(Ad.objects.filter(id=self.ad.id).exists())


class ProposalViewsTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='u1', password='p')
        self.u2 = User.objects.create_user(username='u2', password='p')
        self.ad1 = Ad.objects.create(user=self.u1, title='A1', description='', category='C', condition='X')
        self.ad2 = Ad.objects.create(user=self.u2, title='A2', description='', category='C', condition='X')
        self.client.login(username='u1', password='p')

    def test_create_proposal(self):
        url = reverse('create_proposal', args=[self.ad2.id])
        self.client.get(url)
        response = self.client.post(url, {'ad_sender': self.ad1.id, 'comment': 'Hi'})
        self.assertRedirects(response, reverse('proposal_list'))
        self.assertTrue(ExchangeProposal.objects.filter(ad_sender=self.ad1, ad_receiver=self.ad2).exists())

    def test_update_proposal(self):
        prop = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='x')
        self.client.logout()
        self.client.login(username='u2', password='p')
        url = reverse('update_proposal', args=[prop.id, 'accepted'])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('proposal_detail', args=[prop.id]))
        prop.refresh_from_db()
        self.assertEqual(prop.status, 'accepted')


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', email='john@example.com', password='oldpass')
        self.client.login(username='john', password='oldpass')

    def test_profile_get(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Профиль пользователя')
        # проверяем, что в поле first_name стоит initial=username
        self.assertContains(response, 'value="john"')

    def test_profile_update(self):
        url = reverse('profile')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@new.com',
            'profile_submit': ''
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Данные профиля успешно обновлены.')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john@new.com')

    def test_password_change(self):
        url = reverse('profile')
        data = {
            'old_password': 'oldpass',
            'new_password1': 'newsecurepass',
            'new_password2': 'newsecurepass',
            'password_submit': ''
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароль успешно изменён.')
        self.client.logout()
        login_ok = self.client.login(username='john', password='newsecurepass')
        self.assertTrue(login_ok)


class DeleteProposalTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='u1', password='p1')
        self.u2 = User.objects.create_user(username='u2', password='p2')
        self.ad1 = Ad.objects.create(user=self.u1, title='A1', description='', category='C', condition='X')
        self.ad2 = Ad.objects.create(user=self.u2, title='A2', description='', category='C', condition='X')
        self.prop = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='c')
        self.client.login(username='u2', password='p2')

    def test_delete_proposal_confirmation(self):
        url = reverse('delete_proposal', args=[self.prop.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вы уверены, что хотите удалить это предложение')

    def test_delete_proposal_post(self):
        url = reverse('delete_proposal', args=[self.prop.id])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('proposal_list'))
        self.assertFalse(ExchangeProposal.objects.filter(id=self.prop.id).exists())
