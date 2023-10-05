from django.contrib import admin

from blog.models import Location, Post, Category

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
