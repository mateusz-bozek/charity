from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View

from donation.forms import LoginForm, RegisterForm, ChangePasswordForm, ChangeSettingsForm, DonationForm
from donation.models import Donation, Institution
from users.models import User


class LandingPageView(View):
    def get(self, request):
        donations = Donation.objects.all()
        institutions = Institution.objects.all()
        institutions1 = institutions.filter(type=1)
        institutions2 = institutions.filter(type=2)
        institutions3 = institutions.filter(type=3)

        quantity_bags = 0
        for donation in donations:
            quantity_bags += donation.quantity

        quantity_institutions = len(donations.distinct('institution'))

        return render(request, 'landingpage.html', {'donations': donations,
                                                    'institutions1': institutions1,
                                                    'institutions2': institutions2,
                                                    'institutions3': institutions3,
                                                    'quantity_bags': quantity_bags,
                                                    'quantity_institutions': quantity_institutions})

    def post(self, request):
        return render(request, 'form-confirmation.html')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('logout')

        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landingpage')
            elif User.objects.filter(email=email).exists():
                messages.error(request, f'Niepoprawny email lub hasło')
                return render(request, 'login.html', {'form': form})
            else:
                messages.error(request, f'Użytkownik o adresie email {email} nie istnieje. Zarejestruj się:')
                return redirect('register')
        else:
            messages.error(request, 'Logowanie nieudane')
            return render(request, 'login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('landingpage')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            User.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password)
            return redirect('login')
        else:
            return render(request, 'register.html', {'form': form})


class UserProfileView(View):
    def get(self, request):
        if request.user.is_authenticated:
            donations = Donation.objects.filter(user=request.user).order_by('pick_up_date', 'pick_up_time')
            return render(request, 'profile.html', {'donations': donations})
        return redirect('login')


class UserSettingsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            settings_form = ChangeSettingsForm(
                initial={'user_id': user.id, 'email': user.email, 'first_name': user.first_name,
                         'last_name': user.last_name})
            password_form = ChangePasswordForm(initial={'user_id': user.id})
            return render(request, 'settings.html',
                          {'settings_form': settings_form, 'password_form': password_form})
        return redirect('login')

    def post(self, request):
        user_id = request.user.id
        user = User.objects.get(pk=user_id)

        if 'settings_btn' in request.POST:
            settings_form = ChangeSettingsForm(request.POST)
            if settings_form.is_valid():
                user.first_name = settings_form.cleaned_data['first_name']
                user.last_name = settings_form.cleaned_data['last_name']
                updated_email = settings_form.cleaned_data['email']
                if (updated_email != user.email):
                    if (User.objects.filter(email=updated_email).exists()):
                        messages.error(request, 'Adres email jest już zajęty!')
                        return render(request, 'settings.html', {'settings_form': settings_form,
                                                                 'password_form': ChangePasswordForm(
                                                                     initial={'user_id': user_id})})
                    else:
                        user.email = settings_form.cleaned_data['email']
                user.save()
                return redirect('profile')
        elif 'password_btn' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data['new_password'])
                user.save()
                return redirect('logout')
            else:
                return render(request, 'settings.html', {'settings_form': ChangeSettingsForm(
                    initial={'user_id': user_id, 'email': user.email, 'first_name': user.first_name,
                             'last_name': user.last_name}),
                    'password_form': password_form})
        else:
            redirect('settings')


@login_required(login_url='login')
def AddDonation(request):
    if request.method == 'GET':
        return render(request, 'form.html', {'form': DonationForm(), 'inst': Institution.objects.all()})

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            try:
                don = form.save()
                don.user = request.user
                don.save()
            except Exception as e:
                messages.error(request, f'Błąd: {e}')
                return render(request, 'error.html')
            return render(request, 'form-confirmation.html')
        else:
            messages.error(request, f'Błąd: {form._errors}')
            return render(request, 'error.html')

