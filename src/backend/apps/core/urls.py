from django.urls import path, include
from . import views
from . import adminviews

urlpatterns = [
    path('', views.index, name="index"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('installation/', views.installation, name="installation"),
    path('view/room/<room>', views.viewroom, name="viewroom"),
    
    # Admin views
    path('administration/campus/', adminviews.admin_campus, name="admin_campus"),
    path('administration/add/campus/', adminviews.add_campus, name="add_campus"),
    path('administration/add/room/<campus>', adminviews.add_room, name="add_room"),
    path('administration/add/workstation/<room>', adminviews.add_masive_workstations, name="add_masive_workstations"),
]
