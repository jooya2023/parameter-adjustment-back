from django.contrib.auth.models import Permission
from rest_framework import serializers

from permissions.helper.translate import translate_permission
from permissions.helper.translate_json import filtered_permissions


class ListPermissionSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if isinstance(data, list):
            data = convert_list_to_query(data)

        model_name = []
        app_names = filtered_permissions.keys()
        for key, value in filtered_permissions.items():
            model_name.extend(list(value['models'].keys()))
        filtered_data = data.filter(content_type__app_label__in=app_names, content_type__model__in=model_name)
        ret = super(ListPermissionSerializer, self).to_representation(filtered_data)
        return ret


class CategoryPermissionSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if isinstance(data, list):
            data = convert_list_to_query(data)

        list_category = []

        for key, value in filtered_permissions.items():
            category = {'category': {'name': key, 'translate': value['translate']}}
            filtered_data = data.filter(content_type__model__in=list(value['models'].keys()))
            if filtered_data.count() == 0:
                break
            ret = super(CategoryPermissionSerializer, self).to_representation(filtered_data)
            category['permissions'] = ret
            list_category.append(category)
        return list_category


class PermissionSerializer(serializers.ModelSerializer):
    translate = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('with_category'):
            self.Meta.list_serializer_class = CategoryPermissionSerializer
        else:
            self.Meta.list_serializer_class = ListPermissionSerializer

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'translate']
        list_serializer_class = ListPermissionSerializer

    def get_translate(self, *args, **kwargs):
        return translate_permission(args[0])


def convert_list_to_query(data: list):
    perm_ids = []
    for perm in data:
        perm_ids.append(perm.id)
    return Permission.objects.filter(id__in=perm_ids)