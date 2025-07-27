__all__ = ()

from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import phonenumbers

from contrib.services.rabbit import PhoneNotificationRabbit
from contrib.services.redis import PhoneUserConfirmRedis
from core.trie import CodePrefixTree
from users.managers import CustomUserManager


INVITE_CODE_CONFIG = {
    'alphabet': set('0123456789abcdefghijklmnopqrstuvwxyz'),
    'length': 6,
}
AUTH_CODE_CONFIRM_CONFIG = {
    'alphabet': set('0123456789'),
    'length': 4,
}


class User(auth_models.AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone'
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_(
            '150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        ),
        validators=[auth_models.User.username_validator],
    )
    password = models.CharField(
        _('password'),
        max_length=128,
        blank=True,
        null=True,
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        unique=True,
        help_text=_('+_ (___) ___-__-__'),
    )
    invite_code = models.CharField(
        _('invite code'),
        max_length=6,
        null=True,
        blank=True,
    )
    claimed_invite_code = models.CharField(
        _('claimed invite code'),
        max_length=6,
        null=True,
        blank=True,
    )

    @classmethod
    def normalize_phone(cls, phone):
        phone = phonenumbers.parse(phone)
        return phonenumbers.format_number(
            phone,
            phonenumbers.PhoneNumberFormat.E164,
        )

    @classmethod
    def _gen_unique_code(cls, length, alphabet, existed_codes):
        tree = CodePrefixTree()
        for code in existed_codes:
            tree.insert(code)

        return tree.get_shortest_random(alphabet, length)

    @classmethod
    def clean_phone(cls, phone, pk=None):
        meta_class = cls._meta
        field_name = meta_class.get_field(
            'username',
        ).verbose_name.title()
        try:
            cls.normalize_phone(phone)
        except Exception:
            raise ValidationError(
                _('%(field_name)s field has not valid phone number.'),
                params={'field_name': field_name},
            )

    @classmethod
    def check_confirmation_login_code(cls, code):
        user_id = PhoneUserConfirmRedis.get(code)
        if not user_id:
            return None

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def handle_confirmation_login(self):
        existed_codes = PhoneUserConfirmRedis.list_codes()
        code = self.gen_confirm_login_code(existed_codes)
        self.save_confirm_login_code(code)
        self.send_confirm_login_code(code)

    def send_confirm_login_code(self, code):
        PhoneNotificationRabbit.publish([self.phone], code)

    def save_confirm_login_code(self, code):
        PhoneUserConfirmRedis.publish(self.pk, code)

    def gen_confirm_login_code(self, existed_codes):
        return self._gen_unique_code(
            existed_codes=existed_codes,
            **AUTH_CODE_CONFIRM_CONFIG,
        )

    @transaction.atomic()
    def update_invite_code(self):
        existed_codes = User.objects.select_for_update().values_list(
            User.invite_code.field.name,
            flat=True,
        )
        self.invite_code = self._gen_unique_code(
            existed_codes=existed_codes,
            **INVITE_CODE_CONFIG,
        )

    def save(self, *args, **kwargs):
        self.phone = self.normalize_phone(self.phone)
        if not self.invite_code:
            self.update_invite_code()

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.clean_phone(self.phone, self.pk)
