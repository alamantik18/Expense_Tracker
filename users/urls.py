from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='account_signup'),
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='account_logout'),
    path('email_confirmation/', views.confirmation_email, name='confirmation_email'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    path('password_reset/', views.ResetPassword.as_view(), name='reset_password'),
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]