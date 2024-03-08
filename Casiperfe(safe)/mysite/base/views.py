# coding=utf-8

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm
#from torneos.views import torneos_mantenimiento2 as mm

from django.utils.translation import activate

def activate_language(request):
    myLanguage = request.session.get('myLanguage')
    if not (myLanguage is None):
        activate(myLanguage)

def change_en(request):
    request.session['myLanguage'] = 'en'
    return redirect('home')

def change_es(request):
    request.session['myLanguage'] = 'es'
    return redirect('home')

def change_fr(request):
    request.session['myLanguage'] = 'fr'
    return redirect('home')
    
# Create your views here.
# Home page
def home(request):
    activate_language(request)
    #mm()
    return render(request, 'base/home_t.html')

# signup page
def user_signup(request):
    activate_language(request)
    if request.method == 'POST': 
        # fin edición
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        # crear el html para editar (comienzo de edición)
        form = UserCreationForm()
    # crear el html para editar o error en form
    return render(request, 'base/signup_t.html', {'form': form})

# login page
def user_login(request):
    activate_language(request)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('home')
    else:
        form = LoginForm()
    # crear el html para editar o error en form
    return render(request, 'base/login_t.html', {'form': form})

# logout page
def user_logout(request):
    activate_language(request)
    logout(request)
    return redirect('home')

