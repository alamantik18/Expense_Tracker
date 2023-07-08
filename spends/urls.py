from django.contrib import admin
from django.urls import path, include
from spends import views

urlpatterns = [
    path('home/', views.user_spends, name='my_spends'),
    path('create_spend/', views.CreateSpend.as_view(), name='create_spend'),
    path('view_reports/', views.ViewReports.as_view(), name='view_reports')
]