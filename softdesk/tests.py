from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

import pdb


User = get_user_model()


class UsersAPIViewsTests(APITestCase):

    def test_signup_api_view_password_validation(self):
        pdb.set_trace()
        url = reverse('signup')
        pdb.set_trace()
        body = {'email': 'test_user1@toto.fr', 'password': 'testpass'}
        pdb.set_trace()
        response = self.client.post(url, body, format='json')
        pdb.set_trace()
        self.assertEquals(response.status_code, 400)
