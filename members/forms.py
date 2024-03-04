from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class RegisterUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile', 'address','block','room','profile_image']




# from django.contrib.auth.forms import UserCreationForm
# from .models import User
# from django import forms

# class RegisterUserForm(UserCreationForm):
#     first_name = forms.CharField(max_length=20)
#     last_name = forms.CharField(max_length=20)
#     email = forms.EmailField()
#     phone_number = forms.CharField(max_length=15)

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    