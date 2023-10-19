from django.contrib import admin

from blog.models import Location, Post, Category, Comment

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
admin.site.register(Comment)
