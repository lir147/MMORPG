from django.contrib import admin
from .models import User, Category, Announcement, Response, Newsletter

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Announcement)
admin.site.register(Response)
admin.site.register(Newsletter)