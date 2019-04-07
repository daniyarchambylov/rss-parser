from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import RegistrationForm


class RegistrationView(FormView):
    template_name = 'accounts/registration.html'
    form_class = RegistrationForm
    success_url = '/login/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


def home_view(request):
    return render(request, 'accounts/home.html', locals())
