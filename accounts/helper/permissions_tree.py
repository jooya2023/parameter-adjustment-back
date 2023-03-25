from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _

from permissions.helper.translate import translate_permission
from permissions.helper.translate_json import filtered_permissions


# --- Permissions Tree Functions ---
def _get_apps(permissions: Permission.objects):
    app_names = []
    for perm in permissions:
        app_name = perm.content_type.app_label
        if app_name not in app_names:
            app_names.append(app_name)
    return app_names


def _create_tree(app_name, permissions: Permission.objects, request):
    ignored_permissions = [
    ]
    permissions_list = [
        {
            'id': each_perm.id,
            'name': (each_perm.name,),
            'codename': each_perm.codename,
            "translate": _(each_perm.name),
        }
        for each_perm in permissions
        if each_perm.content_type.app_label == app_name and request.user.has_perm(perm=each_perm)
           and each_perm.codename not in ignored_permissions
    ]
    data = {
        'category': {'name': app_name, 'translate': _(app_name)},
        'permissions': permissions_list,
    }
    return data


def _create_group_tree(app_name, permissions: Permission.objects, group_permissions: Group.objects):
    ignored_permissions = [
    ]
    permissions_list = [
        {
            'id': each_perm.id,
            'name': each_perm.name,
            'codename': each_perm.codename,
            "translate": translate_permission(each_perm),
            'is_active': True if each_perm in group_permissions else False,
        }
        for each_perm in permissions
        if each_perm.content_type.app_label == app_name and each_perm.codename not in ignored_permissions
    ]
    translation = filtered_permissions.get(app_name)
    data = {
        'category': {
            'name': app_name,
            'translate': translation['translate'] if translation else None,
        },
        'permissions': permissions_list,
    }
    return data


def create_permissions_tree(request, permissions: Permission.objects):
    result = []
    for app_name in _get_apps(permissions):
        data = _create_tree(app_name, permissions, request)
        result.append(data)
    return result


def create_permissions_tree_group(permissions: Permission.objects, group_permissions: Group.objects):
    result = []
    ignored_apps = ['contenttypes', 'guardian', 'sessions']
    for app_name in _get_apps(permissions):
        if app_name not in ignored_apps:
            data = _create_group_tree(app_name, permissions, group_permissions)
            result.append(data)
    return result
