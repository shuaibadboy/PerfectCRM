from django.urls import path

from student import views

urlpatterns = [
    path('', views.index, name='student_my_classes'),
    path('studyrecord/<int:class_id>/', views.studyrecord, name='studyrecord'),
    path('homework_detail/<int:studyrecord_id>/', views.homework_detail, name='homework_detail'),
]
