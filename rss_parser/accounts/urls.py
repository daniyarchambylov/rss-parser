from django.contrib.auth.views import LoginView
from . import views as account_views
from django.urls import path


urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('register/', account_views.RegistrationView.as_view(), name='registration'),
    path('', account_views.home_view, name='home'),
]
