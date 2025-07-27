__all__ = ()

from http import HTTPStatus
import time
from unittest.mock import patch

from django.test import override_settings, TestCase
from django.urls import reverse

from mocks.services import rabbit, redis
from users.models import INVITE_CODE_CONFIG, User


class StaticIndexURLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('+71234567890')
        cls.user2 = User.objects.create_user('+71234567892')

    def test_login_on_get(self):
        url = reverse('users:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    @patch('users.models.PhoneUserConfirmRedis', redis.PhoneUserConfirmRedis())
    @patch(
        'users.models.PhoneNotificationRabbit',
        rabbit.PhoneNotificationRabbit(),
    )
    def test_login(self):
        url = reverse('users:login')
        data = {'phone': '+71234567891'}
        response = self.client.post(url, data, 'application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch('users.models.PhoneUserConfirmRedis', redis.PhoneUserConfirmRedis())
    @patch(
        'users.models.PhoneNotificationRabbit',
        rabbit.PhoneNotificationRabbit(),
    )
    def test_login_confirm(self):
        from users.models import PhoneUserConfirmRedis

        old_session_id = self.client.session.session_key
        url = reverse('users:login')
        data = {'phone': self.user.phone}
        self.client.post(url, data, 'application/json')

        code = PhoneUserConfirmRedis.list_codes()[0]
        url = reverse('users:login-confirm')
        data = {'code': code}
        response = self.client.post(url, data, 'application/json')
        new_session_id = self.client.session.session_key
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(old_session_id, new_session_id)

    @patch('users.models.PhoneUserConfirmRedis', redis.PhoneUserConfirmRedis())
    @patch(
        'users.models.PhoneNotificationRabbit',
        rabbit.PhoneNotificationRabbit(),
    )
    @override_settings(REDIS_USER_PHONE_EXPIRATION_TIME=1)
    def test_login_confirm_with_expired_code(self):
        from users.models import PhoneUserConfirmRedis

        url = reverse('users:login')
        data = {'phone': self.user.phone}
        self.client.post(url, data, 'application/json')

        code = PhoneUserConfirmRedis.list_codes()[0]
        time.sleep(1)
        url = reverse('users:login-confirm')
        data = {'code': code}
        response = self.client.post(url, data, 'application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_logout_on_get(self):
        url = reverse('users:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_profile(self):
        self.client.force_login(self.user)
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_unauthorized(self):
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_profile_apply_invite_code(self):
        self.client.force_login(self.user)
        url = reverse('users:profile')
        data = {'claimed_invite_code': self.user2.invite_code}
        response = self.client.put(url, data, 'application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        fetched_user1 = User.objects.get(phone=self.user.phone)
        self.assertEqual(
            fetched_user1.claimed_invite_code,
            self.user2.invite_code,
        )

    def test_profile_apply_wrong_invite_code(self):
        new_code = User._gen_unique_code(
            existed_codes=[self.user.invite_code, self.user2.invite_code],
            **INVITE_CODE_CONFIG,
        )
        self.client.force_login(self.user)
        url = reverse('users:profile')
        data = {'claimed_invite_code': new_code}
        response = self.client.put(url, data, 'application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_profile_apply_invite_code_twice(self):
        self.client.force_login(self.user)
        url = reverse('users:profile')
        data = {'claimed_invite_code': self.user2.invite_code}
        self.user.claimed_invite_code = self.user2.invite_code
        self.user.save()
        response = self.client.put(url, data, 'application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
