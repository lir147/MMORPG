from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from board.views import ckeditor_5_upload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('board.urls')),
    path('ckeditor5/upload/', ckeditor_5_upload, name='ck_editor_5_upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)