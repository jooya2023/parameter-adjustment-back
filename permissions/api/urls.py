from django.urls import path, include

from permissions.api import views

app_name = "permissions"

urlpatterns = [
    path('permissions/', views.ListPermissionUserView.as_view(), name="all-permission-model"),
    path('permissions/<int:id>/', views.PermissionsDetailView.as_view(), name="detail_permission")
]
