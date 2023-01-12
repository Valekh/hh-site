from django import forms
from django.forms import PasswordInput, TextInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        del self.fields['password2']

        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None

        self.fields['username'].label = ""
        self.fields['password1'].label = ""

        self.fields['username'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'})
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ваш пароль'})


class UserLoginForm(AuthenticationForm):
    model = User

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = ""
        self.fields['password'].label = ""

        self.fields['username'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'})
        self.fields['password'].widget = PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ваш пароль'})




