from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)

        if not user or not user.is_admin:
            raise forms.ValidationError('Invalid login credentials')

        return self.cleaned_data
    


# class CustomerCreationForm(UserCreationForm):
#    first_name = forms.CharField(required=True)
#    last_name = forms.CharField(required=True)
#    username = forms.CharField(required=True)
#    email = forms.EmailField(required=True)
     
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

CustomUser = get_user_model()

class CustomerCreationForm(UserCreationForm):
    ...
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
     
#    class Meta:
#       model = CustomUser
#       fields = ("first_name", "email",  "last_name")

#    def __init__(self, *args, **kwargs):
#       super().__init__(*args, **kwargs)
#       self.fields['first_name'].required = True
#       self.fields['last_name'].required = True
      