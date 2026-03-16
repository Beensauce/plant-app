from django.shortcuts import render, redirect
from .forms import RegisterForm

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST) # Binds data with fields
        if form.is_valid():
            form.save() # creates user
            # Redirect to login
            return redirect('login')

    else:
        form = RegisterForm() # creates empty form just in case
    return render(request, 'users/register.html', {'form': form})