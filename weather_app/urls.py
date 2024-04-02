# weather_api_application urls

from django.urls import path
from .import views

urlpatterns = [
    path('api/', views.fetch_data_view, name='metoffice_data'),
    path('data/<str:parameter>/<str:region>/', views.get_region_parameter_data, name='region_parameter_data'),
    path('data-fetch', views.data_fetch, name='data_fetch')
]