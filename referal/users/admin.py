__all__ = ()

from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin as BaseAdmin

from users.models import User


class UserAdmin(BaseAdmin):
    list_display = (
        User.phone.field.name,
        User.invite_code.field.name,
        User.is_active.field.name,
        User.is_staff.field.name,
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[0][1]['fields'] = (
            User.phone.field.name,
            User.username.field.name,
            User.password.field.name,
        )
        self.fieldsets[1][1]['fields'] = (
            User.invite_code.field.name,
            User.first_name.field.name,
            User.last_name.field.name,
            User.email.field.name,
        )


site.register(User, UserAdmin)
