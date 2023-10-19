from django.views.generic import TemplateView
from django.contrib.auth import get_user_model


User = get_user_model()


class AboutTempView(TemplateView):
    template_name = 'pages/about.html'


class RulesTempView(TemplateView):
    template_name = 'pages/rules.html'


class TempView404(TemplateView):
    template_name = 'pages/404.html'

    def get(self, request, exception, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)


class TempView403(TemplateView):
    template_name = 'pages/403csrf.html'

    def get(self, request, exception, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=403)


class TempView500(TemplateView):
    template_name = 'pages/500.html'

    def get(self, request, exception, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=500)
