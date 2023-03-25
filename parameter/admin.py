from django.contrib import admin
from parameter.models import Parameter, FurnaceSetting

# Register your models here.

admin.site.register(Parameter)
admin.site.register(FurnaceSetting)
