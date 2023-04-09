from django.urls import path

from accounts.api import views

app_name = "accounts"

urlpatterns = [
    path("users/", views.UserListAPIView.as_view(), name="user_list"),
    path("users/<int:id>/", views.UserUpdateDetailDeleteAPIView.as_view(), name="user_update_detail_delete"),
    path("users/my/", views.MyUserAPIView.as_view(), name="my_user"),
    path("users/my/update/", views.MyUserUpdateAPIView.as_view(), name="my_update"),

    path('users/login/', views.LoginGenericView.as_view(), name="create_jwt"),
    path('users/logout/', views.LogoutApiView.as_view(), name="logout_user"),
    path('users/register/', views.RegisterGenericView.as_view(), name="register"),
    path("users/change-password/", views.ChangePassword.as_view(), name="change_password"),

    path("token/refresh/", views.CustomRefreshTokenAPIView.as_view(), name="new_token"),

    path('groups/', views.GroupListCreateAPIView.as_view(), name="list_create_group"),
    path('groups/<int:id>/', views.GroupDetailUpdateDeleteAPIView.as_view(), name="detail_update_delete_group"),
    path('groups/<int:id>/users/', views.UsersGroupUpdateAPIView.as_view(), name='user_detail_update_groups'),
]
