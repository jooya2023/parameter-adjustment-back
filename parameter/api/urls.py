from django.urls import path

from parameter.api import views

app_name = "parameter"

urlpatterns = [
    path('api/furnace-setting/', views.FurnaceSettingListCreateAPIView.as_view(), name="list_create_furnace_setting"),
    path('api/furnace-setting/<int:id>/', views.FurnaceSettingRetrieveUpdateDestroyAPIView.as_view(), name="detail_update_delete_furnace_setting"),

    path('api/parameter/', views.ParameterListCreateAPIView.as_view(), name="list_create_parameter"),
    path('api/parameter/<int:id>/', views.ParameterRetrieveUpdateDestroyAPIView.as_view(), name="detail_update_delete_parameter")
]