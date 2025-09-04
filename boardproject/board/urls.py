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
    path('announcement/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('edit/<int:pk>/', views.edit_announcement, name='edit_announcement'),

    path('manage/', views.manage_responses, name='manage_responses'),

    path('response/<int:pk>/', views.submit_response, name='submit_response'),

    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('newsletter/unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    path('newsletter/send/', views.send_newsletter, name='send_newsletter'),
    path('ckeditor5/upload/', views.ckeditor_5_upload_file, name='ck_editor_5_upload_file'),
]