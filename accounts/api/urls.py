from django.urls import path

from accounts.api import views

app_name = "accounts"

urlpatterns = [
    path('api/login/', views.LoginGenericView.as_view(), name="create_jwt")
]