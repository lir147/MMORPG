from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.CustomRegistrationView.as_view(), name='register'),
    path('confirm/', views.ConfirmRegistrationView.as_view(), name='confirm_registration'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('announcement/create/', views.CreateAnnouncementView.as_view(), name='create_announcement'),

    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('newsletter/unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    path('newsletter/send/', views.send_newsletter, name='send_newsletter'),
]