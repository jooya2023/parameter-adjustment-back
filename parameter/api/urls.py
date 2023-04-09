from django.urls import path

from parameter.api import views

app_name = "parameter"

urlpatterns = [
    path('furnace-setting/', views.FurnaceSettingListCreateAPIView.as_view(), name="list_create_furnace_setting"),
    path('furnace-setting/<int:id>/', views.FurnaceSettingRetrieveUpdateDestroyAPIView.as_view(), name="detail_update_delete_furnace_setting"),
    path('furnace-setting/file/<int:id>/', views.ParameterUploadFileAPIView.as_view(), name="upload_excel"),

    path('parameter/', views.ParameterListCreateAPIView.as_view(), name="list_create_parameter"),
    path('parameter/<int:id>/', views.ParameterRetrieveUpdateDestroyAPIView.as_view(), name="detail_update_delete_parameter"),

    path('parameter/calc/', views.ParameterCalculationAPIView.as_view(), name="calc_paramater"),
    path('parameter-factory-api/', views.ParameterApiFactoryAPIView.as_view(), name="parameter_factory_api"),

]