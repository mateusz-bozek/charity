from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


class LandingPageView(View):
    def get(self, request):
        return render(request, 'landingpage.html')

    def post(self, request):
        return render(request, 'form-confirmation.html')


class AddDonationView(View):
    def get(self, request):
        return render(request, 'form.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
