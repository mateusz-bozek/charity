from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from users.models import User


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), validators=[validate_email])
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Imię'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nazwisko'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Ponów hasło'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'is_superuser')

    def clean(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Podany email jest już zajęty!')

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError('Podane hasła nie są identyczne!')

        validate_password(password)


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                             error_messages={'invalid': 'Wpisz poprawny adres email'})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))


class ChangeSettingsForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput)
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                             validators=[validate_email])
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Imię'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Nazwisko'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Aktualne hasło'}))

    def clean(self):
        user_id = self.cleaned_data['user_id']
        password = self.cleaned_data['password']
        user = User.objects.get(pk=user_id)

        if user is None:
            raise forms.ValidationError('Użytkownik nie istnieje')

        if not authenticate(email=user.email, password=password):
            raise forms.ValidationError('Błędne hasło')


class ChangePasswordForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput)
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Stare hasło'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nowe hasło'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Ponów hasło'}))

    def clean(self):
        user_id = self.cleaned_data['user_id']
        old_password = self.cleaned_data['old_password']
        new_password = self.cleaned_data['new_password']
        new_password2 = self.cleaned_data['new_password2']
        user = User.objects.get(pk=user_id)

        if user is None:
            raise forms.ValidationError('Użytkownik nie istnieje')

        if not authenticate(email=user.email, password=old_password):
            raise forms.ValidationError('Błędne stare hasło')

        if new_password != new_password2:
            raise forms.ValidationError('Powtórzone hasło nie zgadza się!')

        validate_password(new_password)
