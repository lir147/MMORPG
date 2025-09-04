from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.CustomRegistrationView.as_view(), name='register'),
    path('confirm/', views.confirm_registration, name='confirm_registration'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create/', views.create_announcement, name='create_announcement'),
    path('edit/<int:pk>/', views.edit_announcement, name='edit_announcement'),
    path('announcement/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('response/<int:pk>/', views.submit_response, name='submit_response'),
    path('manage/', views.manage_responses, name='manage_responses'),
    path('my-responses/', views.my_responses, name='my_responses'),
    path('response/<int:response_id>/accept/', views.accept_response, name='accept_response'),
    path('response/<int:response_id>/delete/', views.delete_response, name='delete_response')
]