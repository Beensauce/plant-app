from django.urls import path
from . import views # Importing functions to run when a specific URL is reached

# Linking my views, of what the user will see to a specific URL address
urlpatterns = [
    path('', views.index, name='main'), # So here, website.com will run the index function
    path('tracker/', views.add_health_log, name='tracker'), # Here, if website.com/tracker will run the add health log function
    path('tracker/<int:plant_id>', views.add_health_log, name='tracker_with_id'),
    path('plants/', views.PlantListView.as_view(), name='plants'),
    path('plants/water/<int:plant_id>', views.water_plant, name='water_plant'),
    path('plant/<int:pk>/delete/', views.DeletePlantListView.as_view(), name='delete_plant'),
    path('tracker/<int:pk>/delete', views.DeleteTrackListView.as_view(), name='delete_track'),
    path('plants/detail/<int:plant_id>', views.plant_detail, name='plant-detail'),
    path('plants/edit/<int:plant_id>/', views.edit_plant, name='edit-plant'),
    path('plants/health-assesment/<int:pk>', views.health_assesment, name='health-assesment')
]
