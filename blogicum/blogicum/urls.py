from django.conf import settings
from django.contrib import admin
from django.urls import path, include

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
