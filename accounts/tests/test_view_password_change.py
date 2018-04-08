from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.urls import resolve,reverse
from django.test import TestCase

class LoginRequiredPasswordChangeTests(TestCase):
	def test_redirection(self):
		url = reverse('password_change')
		login_url = reverse('login')
		response = self.client.get(url)
		self.assertRedirects(response,'{login_url}?next={url}'.format(login_url=login_url,url=url))


class PasswordChangeTestCase(TestCase):
	def setUp(self,data={}):
		self.user = User.objects.create_user(username='leo',email='leo.huangyy@qq.com',password='old_password')
		self.url = reverse('password_change')
		self.client.login(username='leo',password='old_password')
		self.response = self.client.post(self.url,data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
	def setUp(self):
		super().setUp({
			'old_password':'old_password',
			'new_password1':'new_password',
			'new_password2':'new_password',
			})

	def test_redirection(self):
		self.assertRedirects(self.response,reverse('password_change_done'))


	def test_password_changed(self):
		'''
		refr
		esh the user instance from database to get the new password
		hash updated by the change password view.
		'''
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('new_password'))

	def test_user_authentication(self):
		response = self.client.get(reverse('home'))
		user = response.context.get('user')
		self.assertTrue(user.is_authenticated)

class InvalidPasswordChangeTests(PasswordChangeTestCase):
	def test_status_code(self):
		self.assertEqual(self.response.status_code,200)

	def test_form_errors(self):
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

	def test_didnt_change_password(self):
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('old_password'))





