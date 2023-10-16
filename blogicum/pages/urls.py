from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutTempView.as_view(), name='about'),
    path('rules/', views.RulesTempView.as_view(), name='rules'),
    path('404/', views.TempView404.as_view(), name='404'),
    path('403csrf/', views.TempView403.as_view(), name='403csrf'),
    path('500/', views.TempView500.as_view(), name='500'),
]
