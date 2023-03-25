from django_property_filter import PropertyFilterSet, PropertyCharFilter

from permissions.models import PermissionProxy


class PermissionFilterSet(PropertyFilterSet):

    class Meta:
        model = PermissionProxy
        fields = []
        property_fields = [('translate', PropertyCharFilter, ['contains'])]
