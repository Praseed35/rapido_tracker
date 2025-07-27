from django.contrib import admin
from django.urls import path
from rides import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='home'),  # This is now the home page
    path('add-ride/', views.add_ride, name='add_ride'),
    path('petrol/', views.update_petrol, name='update_petrol'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('ride/<int:ride_id>/edit/', views.edit_ride, name='edit_ride'),
    path('ride/<int:ride_id>/delete/', views.delete_ride, name='delete_ride'),
]