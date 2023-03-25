from django.contrib.auth.models import Permission

from permissions.helper.translate import translate_permission


class PermissionProxy(Permission):

    @property
    def translate(self):
        return translate_permission(self.name)

    class Meta:
        proxy = True
        default_permissions = ()
