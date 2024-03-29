# weather_api_application urls

from django.urls import path
from .import views

urlpatterns = [
    path('api/', views.fetch_data_view, name='metoffice_data'),
    path('year-value/<int:year>/<str:parameter>/<str:region>/', views.get_yearwise_data, name='get_yearwise_data'),
]
