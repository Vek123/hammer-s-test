__all__ = ()

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def _create_user_object(self, phone, email, password, **extra_fields):
        if not phone:
            raise ValueError('The given username must be set')

        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(  # NoQa
            self.model._meta.app_label,
            self.model._meta.object_name,
        )
        phone = GlobalUserModel.normalize_phone(phone)
        user = self.model(phone=phone, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, phone, email, password, **extra_fields):
        return super()._create_user(phone, email, password, **extra_fields)

    async def _acreate_user(self, phone, email, password, **extra_fields):
        return await super()._acreate_user(
            phone,
            email,
            password,
            **extra_fields,
        )

    def create_user(self, phone, email=None, password=None, **extra_fields):
        return super().create_user(
            phone,
            email,
            password,
            **extra_fields,
        )

    async def acreate_user(
        self,
        phone,
        email=None,
        password=None,
        **extra_fields,
    ):
        return await super().acreate_user(
            phone,
            email,
            password,
            **extra_fields,
        )

    def create_superuser(
        self,
        phone,
        email=None,
        password=None,
        **extra_fields,
    ):
        return super().create_superuser(phone, email, password, **extra_fields)

    async def acreate_superuser(
        self,
        phone,
        email=None,
        password=None,
        **extra_fields,
    ):
        return await super().acreate_superuser(
            phone,
            email,
            password,
            **extra_fields,
        )
