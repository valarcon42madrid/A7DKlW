# coding=utf-8
   
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from base.views import  activate_language
from .models import Torneo, FaseTorneo
from .forms import TorneoForm
import datetime
import random
import re

"""
from itertools import chain
def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data
"""

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

def torneos_mantenimiento(request):
	torneos_mantenimiento2()
	r1 = torneo_jugar(1)
	r2 = torneo_jugar(2)
	r3 = torneo_jugar(3)
	r4 = torneo_jugar(4)
	print(r1)
	print(r2)
	print(r3)
	print(r4)	
	#torneo_result(1, 1, 3, 4, 15, 20)
	#torneo_result(1, 2, 4, 2, 12, 20)	
	#torneo_result(2, 1, 2, 3, 20, 11)
	#torneo_result(4, 1, 3, 2, 10, 20)
	#torneo_result(4, 2, 1, 2, 20, 0)
	return redirect('home')

def torneos_mantenimiento2(): # esto hay que ejecutarlo periodicamente o cuando alguien entre en la página de inicio
	t = datetime.datetime.now()
	torneos = Torneo.objects.filter(fin_inscripcion__lt=t, terminado=False)
	for torneo in torneos:
		# print(torneo)
		fase_actual = torneo.fase_actual
		fase_calculada = torneo.getFase()
		if fase_calculada > fase_actual:
			print('mantenimiento de torneo ' + torneo.nombre)
			torneo_nuevaFase(torneo)

def torneo_nuevaFase(torneo):
	fase_actual = torneo.fase_actual
	if fase_actual == 0:
		jugadores = torneo.jugadores
	else:
		faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)
		jugadores = faseTorneo.ganadores
		lista_partidos_resultados = faseTorneo.lista_partidos_resultados
		if "{" in lista_partidos_resultados:
			return # sin acabar la fase actual
	list = []
	for jugador in jugadores.all():
		t = ( jugador.id, random.random() ) # orden aleatorio
		list.append(t)
	if len(list) == 0:
		print('todavía no están los jugadores')
		return
	if len(list) == 1:
		print('hay un ganador')
		torneo.terminado = True
		torneo.save()
		return
	fSortListOfTuple(list)
	fase_actual += 1
	faseTorneo = FaseTorneo() # nuevo
	faseTorneo.torneo = torneo
	faseTorneo.fase = fase_actual
	faseTorneo.save() # provisional save to add jugadores
	#
	faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual) # toma el mismo registro
	pasaUltimoJugador = False
	n = 0
	lp = "[ "
	for jn in list:
		j = jn[0]
		user = User.objects.get(id=j)
		faseTorneo.jugadores.add(user) # add to jugadores
		if n % 2 == 0:
			if n != 0:
				lp += ", "
			lp  += "( " + user.username + " {" +  str(user.id) + "}"
		else:
			lp += ", " + user.username + " {" + str(user.id) + "} )"
		n += 1	
	if n % 2 == 1:
		lp += " )"
		pasaUltimoJugador = True
	lp += " ]"
	print(lp)
	lp1 = lp
	if pasaUltimoJugador:
		s1 = "{" +  str(user.id) + "}"
		lp1 = lp.replace(s1, "*")
		faseTorneo.ganadores.add(user)	
	lp2 = re.sub( "{[0-9]+}", "", lp)
	#print(lp2)
	faseTorneo.lista_partidos = lp2
	faseTorneo.lista_partidos_resultados = lp1
	faseTorneo.save()
	torneo.fase_actual = fase_actual
	torneo.save()

def torneos_info_list(request):
	torneos2 = []
	torneo2 = {}
	torneos = Torneo.objects.all().order_by('comienzo_partidos')
	for torneo in torneos:
		idTorneo = torneo.id
		#print(torneoId)
		#print(torneo.nombre)
		#print(to_dict(torneo))
		fasesTorneo = FaseTorneo.objects.filter(torneo=idTorneo).order_by('fase')
		for faseTorneo in fasesTorneo:
			lpr1 = faseTorneo.lista_partidos_resultados
			lpr2 = re.sub( "{[0-9]+}", "", lpr1)
			faseTorneo.lista_partidos_resultados = lpr2
		#print(to_dict(fasesTorneo[0]))
		#print(fasesTorneo[0].lista_partidos)
		torneo2 = {}
		torneo2['copy'] = torneo
		torneo2['fases'] = fasesTorneo
		torneos2.append(torneo2)
	return render(request, 'torneos/torneos_info_t.html',  {'torneos': torneos2})

"""
def torneo_pasa(idTorneo, fase, idJugador): # no se usa solo para pruebas
	try:
		faseTorneo = FaseTorneo.objects.get(torneo=idTorneo, fase=fase)
	except FaseTorneo.DoesNotExist:
		return
	user = User.objects.get(id=idJugador)
	faseTorneo.ganadores.add(user)
	s1 = "{" +  str(user.id) + "}"
	lpr =	faseTorneo.lista_partidos_resultados
	lpr2 = lpr.replace(s1, "*")
	faseTorneo.lista_partidos_resultados = lpr2
	faseTorneo.save()
"""

def torneo_jugar(idJugador):
	# t = datetime.datetime.now() + datetime.timedelta(minute=1)
	torneos = Torneo.objects.filter(terminado=False)
	user = User.objects.get(id=idJugador)
	sUser = "{" + str(idJugador) + "}"
	for torneo in torneos:
		if not torneo.esHoraDeEmpezar():
			continue
		# print(torneo)
		fase_actual = torneo.fase_actual
		if fase_actual == 0:
			continue
		faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)
		lpr = faseTorneo.lista_partidos_resultados
		if sUser in lpr:
			return True
	return False
	
def torneo_result(idTorneo, fase, idJugador1, idJugador2, puntos1, puntos2):
	try:
		faseTorneo = FaseTorneo.objects.get(torneo=idTorneo, fase=fase)
	except FaseTorneo.DoesNotExist:
		return
	n = 0
	pj1 = -1
	pj2 = -1
	for jugador in faseTorneo.jugadores.all():
		if jugador.id == idJugador1:
			pj1 = n
		if jugador.id == idJugador2:
			pj2 = n
		n+=1
	#if not faseTorneo.jugadores.filter(id=idJugador1).exists():
	if pj1 == -1:
		return
	#if not faseTorneo.jugadores.filter(id=idJugador2).exists():
	if pj2 == -1:
		return
	dif = abs(pj1 - pj2)
	if dif != 1:
		return
	s1 = "{" + str(idJugador1) +  "}"
	s2 = "{" + str(idJugador2) +  "}"
	lpr = faseTorneo.lista_partidos_resultados
	if puntos1 >= puntos2:
		m1 = " *"
		m2 = ""
		user1 = User.objects.get(id=idJugador1)
		faseTorneo.ganadores.add(user1)
	else:
		m1 = ""
		m2 = " *"
		user2 = User.objects.get(id=idJugador2)
		faseTorneo.ganadores.add(user2)
	r1 = str(puntos1) + m1
	r2 = str(puntos2) + m2
	lpr2 = lpr.replace(s1, r1).replace(s2, r2)
	faseTorneo.lista_partidos_resultados = lpr2
	faseTorneo.save()
	return
	
	
	
	
	