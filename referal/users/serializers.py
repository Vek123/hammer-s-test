__all__ = ()

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from users.models import AUTH_CODE_CONFIRM_CONFIG, User


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (User.phone.field.name,)
        extra_kwargs = {
            'phone': {'validators': []},
        }

    def validate(self, attrs):
        User.clean_phone(attrs[User.phone.field.name])
        return attrs


class LoginConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=AUTH_CODE_CONFIRM_CONFIG['length'],
        min_length=AUTH_CODE_CONFIRM_CONFIG['length'],
        required=True,
        write_only=True,
    )

    def validate_code(self, value):
        if set(value).difference(AUTH_CODE_CONFIRM_CONFIG['alphabet']):
            raise serializers.ValidationError(
                _('Code should contain only numbers or letters'),
            )

        return value


class ProfileSerializer(serializers.ModelSerializer):
    invites = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            User.phone.field.name,
            User.invite_code.field.name,
            User.claimed_invite_code.field.name,
            'invites',
        )
        extra_kwargs = {
            User.phone.field.name: {'read_only': True},
            User.invite_code.field.name: {'read_only': True},
        }

    def get_invites(self, obj):
        return User.objects.filter(
            claimed_invite_code=obj.invite_code,
        ).values_list(
            User.phone.field.name,
            flat=True,
        )

    def validate_claimed_invite_code(self, value):
        if self.instance.claimed_invite_code:
            raise serializers.ValidationError(
                _("You can't delete or change claimed invite code"),
            )

        if not User.objects.filter(invite_code=value).exists():
            raise serializers.ValidationError(
                _("Written invite code doesn't exist"),
            )

        return value
