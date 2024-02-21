"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.views.decorators.csrf import csrf_exempt #nuevo

from myapp import views, ru_views

urlpatterns = [
    #path('admin/', admin.site.urls), # ya estaba
    path('', ru_views.home, name='home'),
    path('login', ru_views.user_login, name='login'),
    path('signup', ru_views.user_signup, name='signup'),
    path('logout', ru_views.user_logout, name='logout'),
    #path('', views.mi_html1), # enviar fichero de prueba
    #path('h2', views.mi_html2), # enviar fichero de prueba
    #path('h3', views.mi_html3), # enviar fichero de prueba
    #path('h4', views.mi_html4), # enviar fichero de prueba
    #path('h5', views.mi_html5), # enviar fichero de prueba
    path("arranque", views.fun_arranque, name='arranque'), 
    path("aj_keys", csrf_exempt(views.fun_keys)),
    path('aj_status', csrf_exempt(views.fun_status)),
]

"""
    path('', views.index, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
"""

# views.fun_arranque es la funcion fun_arranque del modulo view
# arranque = url que arranca el partido
# key     = url para comunicacion ajax entre el javascript del navegador y el servidor.
#                el navegador envia las teclas que pulsa el usuario para mover su jugador
# status = url para comunicacion ajax entre el javascript del navegador y el servidor.
#               el navegador pide al servidor el estado del partido (posicion de pelota, jugadores, marcador, etc.).