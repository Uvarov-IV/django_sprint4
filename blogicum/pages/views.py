from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

class UserRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = "pages/registration.html"
    success_url = reverse_lazy("pages:about")


@requires_csrf_token
def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def server_error(request):
    return render(request, "pages/500.html", status=500)
