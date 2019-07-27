from django.urls import path

from crm import views

urlpatterns = [
    path('', views.index, name='sale_index'),
    path('customer/<int:customer_id>/enrollment/', views.enrollment, name='enrollment'),
    path('customer/<int:enrollment_id>/enrollment_rejection/', views.enrollment_rejection, name='enrollment_rejection'),
    path('contract_review/<int:enrollment_id>/', views.contract_review, name='contract_review'),
    path('payment/<int:enrollment_id>/', views.payment, name='payment'),
    path('customer/registration/<int:enrollment_id>/<str:random_str>/', views.stu_registration, name='stu_registration'),
    path('customer/', views.customer_list, name='customer_list'),
]
