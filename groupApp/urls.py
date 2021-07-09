from django.urls import path
from . import views 


urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('main_page', views.main_page),
    path('create', views.create_group),
    path('group/<int:group_id>', views.show_group),
    path('groups/join/<int:group_id>', views.joined_groups),
    path('groups/leave/<int:group_id>', views.leave_group),
    path('groups/delete/<int:group_id>', views.delete_group),
]