from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.conf.urls.static import static
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.contrib import admin

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.error_500'

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('pages:homepage'),
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
