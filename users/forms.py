from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Defining user registration form
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']