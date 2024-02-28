from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from base.views import  activate_language
from .models import Torneo, FaseTorneo
from .forms import TorneoForm
import datetime
import random

# Create your views here.

def torneos_inscripcion_list(request):
	activate_language(request)
	if not request.user.is_authenticated:
		return
	t = datetime.datetime.now()
	#torneos = Torneo.objects.all().order_by('comienzo_partidos')
	torneos = Torneo.objects.filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t).order_by('comienzo_partidos')
	context = {'torneos': torneos, 'user': request.user, }
	return render(request, 'torneos/torneos_inscripcion_t.html', context)

def torneos_inscripcion(request):
	if not request.user.is_authenticated:
		return	
	idTorneo = int(request.GET.get('idTorneo'))
	idUser = int(request.GET.get('idUser'))
	torneo = Torneo.objects.get(id=idTorneo)
	user = User.objects.get(id=idUser)
	if torneo.jugadores.filter(id=idUser).exists():
		torneo.jugadores.remove(user)
	else:
		torneo.jugadores.add(user)
	torneo.save()
	return redirect('torneos_inscripcion_list')

def torneos_admin(request):
	activate_language(request)
	if not request.user.is_superuser: 
		return
	t = datetime.datetime.now()
	torneos = Torneo.objects.all().order_by('comienzo_partidos')
	#torneos = Torneo.objects.filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t).order_by('comienzo_partidos')
	context = {'torneos': torneos, }
	return render(request, 'torneos/torneos_admin_t.html', context)
		
def torneos_delete(request):
	if not request.user.is_superuser: 
		return
	idTorneo = request.GET.get('idTorneo')
	torneo = Torneo.objects.get(id=idTorneo)
	torneo.delete()
	return redirect('torneos_admin')
	
def torneos_edit(request):
	activate_language(request)
	if not request.user.is_superuser: 
		return
	if request.method == 'POST':
		# print("edición terminada -> hay que salvar (modificar o insertar nuevo)")
		idTorneo = int(request.POST.get('idTorneo'))
		form = TorneoForm(request.POST) # datos procedentes del form
		if form.is_valid():
			cd = form.cleaned_data # datos procedentes del form
			if idTorneo != -1: # modify
				torneo = Torneo.objects.get(id=idTorneo) # get torneo
				torneo.nombre = cd['nombre']
				torneo.comienzo_inscripcion = cd['comienzo_inscripcion']
				torneo.fin_inscripcion = cd['fin_inscripcion']
				torneo.comienzo_partidos = cd['comienzo_partidos']
				torneo.minutos_entre_partidos = cd['minutos_entre_partidos']
				print("salva modificación")
				torneo.save()
			else: # new
				torneo = Torneo() # new torneo
				torneo.setDateTimes()
				print(torneo)
				torneo.nombre = cd['nombre']
				torneo.comienzo_inscripcion = cd['comienzo_inscripcion']
				torneo.fin_inscripcion = cd['fin_inscripcion']
				torneo.comienzo_partidos = cd['comienzo_partidos']
				torneo.minutos_entre_partidos = cd['minutos_entre_partidos']
				print("salva nuevo")
				torneo.save()
			return redirect('torneos_admin')
	else:
		# crear el html para editar (comienzo de edición)
		idTorneo = request.GET.get('idTorneo')
		if not (idTorneo is None):  # modificar
			# print("html para modificar")
			idTorneo = int(idTorneo)
			torneo = Torneo.objects.get(id=idTorneo)
			dd = {
				'nombre': torneo.nombre, 
				'comienzo_inscripcion': torneo.comienzo_inscripcion,
				'fin_inscripcion': torneo.fin_inscripcion,
				'comienzo_partidos': torneo.comienzo_partidos,
				'minutos_entre_partidos': torneo.minutos_entre_partidos
			}
			form = TorneoForm(initial=dd)
		else: # nuevo
			# print("html para añadir nuevo")
			idTorneo = -1 
			torneo = Torneo() # vacío
			torneo.setDateTimes()
			dd = {
				'nombre': torneo.nombre, 
				'comienzo_inscripcion': torneo.comienzo_inscripcion,
				'fin_inscripcion': torneo.fin_inscripcion,
				'comienzo_partidos': torneo.comienzo_partidos,
				'minutos_entre_partidos': torneo.minutos_entre_partidos
			}
			form = TorneoForm(initial=dd) 
	# crear el html para editar o error en form
	return render(request, 'torneos/torneos_edit_t.html', {'form': form, 'idTorneo': idTorneo})

# Python program to sort a list of
# tuples by the second Item using sort() 
# Function to sort the list by second item of tuple
def fSortListOfTuple(listOfTuple): 
    # reverse = None (Sorts in Ascending order) 
    # key is set to sort using second element of 
    # sublist lambda has been used 
    listOfTuple.sort(key = lambda x: x[1]) 
    return listOfTuple

def torneos_maintenance(request):
	torneos_maintenance2()
	return redirect('home')

def torneos_maintenance2(): # esto hay que ejecutarlo periodicamente o cuando alguien entre en la página de inicio
	t = datetime.datetime.now()
	torneos = Torneo.objects.filter(fin_inscripcion__lt=t, terminado=False)
	for torneo in torneos:
		# print(torneo)
		fase_actual = torneo.fase_actual
		fase_calculada = torneo.getFase()
		if fase_calculada > fase_actual:
			torneo_nuevaFase(torneo)
			torneo.fase_actual = fase_actual + 1
			torneo.save()

def torneo_nuevaFase(torneo):
	fase_actual = torneo.fase_actual
	if fase_actual == 0:
		jugadores = torneo.jugadores
	else:
		jugadores = FaseTorneo.object.filter(torneo=torneo.id, fase=fase_actual).ganadores
	list = []
	for jugador in jugadores.all():
		t = ( jugador.id, random.random() ) # orden aleatorio
		list.append(t)
	fSortListOfTuple(list)
	#
	faseTorneo = FaseTorneo() # nuevo
	faseTorneo.torneo = torneo
	faseTorneo.fase = fase_actual + 1
	faseTorneo.save()
	n = 0
	lp = "[ "
	for jn in list:
		j = jn[0]
		user = User.objects.get(id=j)
		faseTorneo.jugadores.add(user) # add to jugadores
		if n % 2 == 0:
			if n != 0:
				lp += ", "
			lp  += "( " + user.username + ", "
		else:
			lp += user.username + " )"
		n += 1	
	if n % 2 == 1:
		lp += " )"
	lp += " ]"
	print(lp)
	faseTorneo.lista_partidos = lp
	faseTorneo.save()
	