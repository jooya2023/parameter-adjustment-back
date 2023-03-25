from django.urls import path

from accounts.api import views

app_name = "accounts"

urlpatterns = [
    path('api/login/', views.LoginGenericView.as_view(), name="create_jwt"),

    path('api/groups/', views.GroupListCreateAPIView.as_view(), name="list_create_group"),
    path('api/groups/<int:id>/', views.GroupDetailUpdateDeleteAPIView.as_view(), name="detail_update_delete_group"),
    path('api/groups/<int:id>/users/', views.UsersGroupUpdateAPIView.as_view(), name='user_detail_update_groups'),
]