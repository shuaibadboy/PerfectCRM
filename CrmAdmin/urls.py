from django.urls import path

from CrmAdmin import views

urlpatterns = [
    path('', views.index, name='table_index'),
    path('<str:app>/', views.tables_of_app, name='tables_of_app'),
    path('<str:app>/<str:table>/', views.display_table_objs, name='table_objs'),
    path('<str:app>/<str:table>/<int:obj_id>/change/', views.table_obj_change, name='table_obj_change'),
    path('<str:app>/<str:table>/<int:obj_id>/change/password/', views.password_reset, name='password_reset'),
    path('<str:app>/<str:table>/<int:obj_id>/delete/', views.table_obj_delete, name='table_obj_delete'),
    path('<str:app>/<str:table>/add/', views.table_obj_add, name='table_obj_add'),
]
