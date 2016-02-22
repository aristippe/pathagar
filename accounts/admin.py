from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin

from userena.models import UserenaSignup
from userena import settings as userena_settings
from userena.utils import get_profile_model, get_user_model


class UserenaSignupInline(admin.StackedInline):
    model = UserenaSignup
    max_num = 1


class UserenaAdmin(UserAdmin, GuardedModelAdmin):
    inlines = [UserenaSignupInline, ]
    list_display = (_('username'), _('email'), _('first_name'), _('last_name'),
                    _('is_staff'), _('is_active'), _('date_joined'))
    list_filter = (_('is_staff'), _('is_superuser'), _('is_active'))


if userena_settings.USERENA_REGISTER_USER:
    try:
        admin.site.unregister(get_user_model())
    except admin.sites.NotRegistered:
        pass

    admin.site.register(get_user_model(), UserenaAdmin)

if userena_settings.USERENA_REGISTER_PROFILE:
    admin.site.register(get_profile_model(), GuardedModelAdmin)
