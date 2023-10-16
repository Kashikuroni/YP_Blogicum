from django.views.generic import TemplateView
from django.contrib.auth import get_user_model


User = get_user_model()


class AboutTempView(TemplateView):
    template_name = 'pages/about.html'


class RulesTempView(TemplateView):
    template_name = 'pages/rules.html'


class TempView404(TemplateView):
    template_name = 'pages/404.html'


class TempView403(TemplateView):
    template_name = 'pages/403csrf.html'


class TempView500(TemplateView):
    template_name = 'pages/500.html'
