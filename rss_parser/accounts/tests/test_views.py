from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import datetime
from rss_parser.feeds.models import Feed, FeedArticle


User = get_user_model()


class LoginViewTestCase(TestCase):
    def test_200(self):
        response = self.client.get('/login/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')



class RegistrationViewTestCase(TestCase):
    def test_get_200(self):
        response = self.client.get('/register/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')

    def test_user_created(self):
        response = self.client.post('/register/', { 'username': 'test-user', 'password1': 'test-password', 'password2': 'test-password' })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/login/')
        self.assertEquals(User.objects.filter(username='test-user').count(), 1)
