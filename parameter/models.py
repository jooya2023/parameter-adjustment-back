from django.db import models


# Create your models here.

class FurnaceSetting(models.Model):
    name = models.CharField(max_length=250)
    data = models.JSONField()
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=250)
    data = models.JSONField()
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class ParameterCalc(models.Model):
    data = models.JSONField()
    furnace_setting = models.ForeignKey(FurnaceSetting, on_delete=models.CASCADE, related_name="furnace_setting")
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="parameter")
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
