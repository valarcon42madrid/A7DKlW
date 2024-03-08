# coding=utf-8

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
#from django.contrib.auth import authenticate, login, logout 
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
#from django.template.loader import get_template
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate
from django.db.models import Q, F
from .models import Partido_enJuego, Partido_historia
from torneos.views import torneo_jugar, torneo_result
from general.views import activate_language
import datetime

# constantes globales

campo = { "ancho": 800, "alto": 400 }
sep = 15 # separacion del jugador con el fondo de la pista
raqueta = { "ancho": 10, "alto": 80 }
pelota = { "ancho": 15, "alto": 15 }

jugador1_x = 0 - campo["ancho"] / 2 + sep # 0 = centro
jugador2_x = 0 + campo["ancho"] / 2 - sep # 0 = centro

min_y = - campo["alto"] / 2
max_y = campo["alto"] / 2
min_x = - campo["ancho"] / 2
max_x = campo["ancho"] / 2

dist_x = (raqueta["ancho"] + pelota["ancho"]) / 2
dist_y = (raqueta["alto"] + pelota["alto"]) / 2

jugador1_rebote_raqueta = jugador1_x + raqueta["ancho"] / 2
jugador2_rebote_raqueta = jugador2_x - raqueta["ancho"] / 2

max_puntuacion = 20

jugador_velocidad = 120
pelota_velocidad = 90

def fLimit(val, min, max):
	r = val
	if val < min:
		r = min
	if val > max:
		r = max
	return r

def diffTimeSec(t1, t2):
	s = t2.timestamp() - t1.timestamp()
	#s = dt.seconds
	#ms = dt.microseconds
	#ss = s + ms / 1e6
	return s

# Para el jugador 1 del partido: actualiza la posicion, cambia el update
def fMoverJugador1(partido):
	t1 = partido.jugador1_actualizacion
	t2 = datetime.datetime.now()
	s = diffTimeSec(t1, t2)
	#print("j1 seconds="	+ str(s))
	new_y = partido.jugador1_y + partido.jugador1_velocidad_y * s
	new_y = fLimit(new_y, min_y, max_y)
	partido.jugador1_y = new_y
	partido.jugador1_actualizacion = t2

# Para el jugador 1 del partido: anota la nueva velocidad segun la tecla
def fKeyJugador1(partido, key):
	if key == "up_end" or key == "down_end":
		partido.jugador1_velocidad_y = 0
	elif key == "down_begin":
		partido.jugador1_velocidad_y = jugador_velocidad
		#print("j1 down vvvvvvvvvvvvvvvvvvvvvvvvvv")
	elif key == "up_begin":
		partido.jugador1_velocidad_y = - jugador_velocidad
		#print("j1 up ^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		
# Para el jugador 2 del partido: actualiza la posicion, cambia el update
def fMoverJugador2(partido):
	t1 = partido.jugador2_actualizacion
	t2 = datetime.datetime.now()
	s = diffTimeSec(t1, t2)
	#print("j2 seconds="	+ str(s))
	new_y = partido.jugador2_y + partido.jugador2_velocidad_y * s
	new_y = fLimit(new_y, min_y, max_y)
	partido.jugador2_y = new_y
	partido.jugador2_actualizacion = t2

# Para el jugador 2 del partido: anota la nueva velocidad segun la tecla
def fKeyJugador2(partido, key):
	if key=="up_end" or key == "down_end":
		partido.jugador2_velocidad_y = 0
	elif key == "down_begin":
		partido.jugador2_velocidad_y = jugador_velocidad
		#print("j2 down vvvvvvvvvvvvvvvvvvvvvvvvvv")
	elif key == "up_begin":
		partido.jugador2_velocidad_y = - jugador_velocidad
		#print("j2 up ^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

# mensaje Key = idPartido + ";" + numJugador + ";" + key
# key: down_begin, down_end, up_begin, up_end
def fRecibirKey(mensajeKey):
	aMensajeKey = mensajeKey.split(";")
	idPartido = int(aMensajeKey[0])
	numJugador = int(aMensajeKey[1]) # 0 o 1
	key = aMensajeKey[2]
	try:
		partido = Partido_enJuego.objects.get(id=idPartido)
	except Partido_enJuego.DoesNotExist:
		return
	if numJugador == 1:
		fMoverJugador1(partido)
		fKeyJugador1(partido, key)
	elif numJugador == 2:
		fMoverJugador2(partido)	
		fKeyJugador2(partido, key)		
	partido.save() # modifica el partido

def fJugador1TocaPelota(partido):
	if abs(partido.pelota_x - jugador1_x) > dist_x:
		return False
	if abs(partido.pelota_y - partido.jugador1_y) > dist_y:
		return False
	if partido.pelota_x < jugador1_x:
		return False
	return True

def fJugador2TocaPelota(partido):
	if abs(partido.pelota_x - jugador2_x) > dist_x:
		return False
	if abs(partido.pelota_y - partido.jugador2_y) > dist_y:
		return False
	if partido.pelota_x > jugador2_x:
		return False
	return True

def fPartidoAnotarResultado(partido):
	# partido = Partido_enJuego
	print("anotar resultado partido")
	if partido.tipo == "R": # partido rápido
		partido2 = Partido_historia() # nuevo
		partido2.jugador1 = partido.jugador1
		partido2.jugador2 = partido.jugador2
		partido2.jugador1_marcador = partido.jugador1_marcador
		partido2.jugador2_marcador = partido.jugador2_marcador
		partido2.comienzo = partido.comienzo
		partido2.fin = partido.fin 
		partido2.save()
	elif partido.tipo == "T": # Torneo
		torneo_result(
			partido.idTorneo, partido.nFaseTorneo, 
			partido.jugador1.id, partido.jugador2.id, 
			partido.jugador1_marcador, partido.jugador2_marcador
		)
	
def fMoverPelota(partido):
	t2 = datetime.datetime.now()
	if partido.tipo == "T" and partido.limiteTiempoTorneo < t2:
		partido.terminado = True
		partido.fin = t2
		fPartidoAnotarResultado(partido)
		return
	if partido.tipo == "T" and (partido.estadoTorneo == "1" or partido.estadoTorneo == "2") and partido.limiteTiempoConUnJugador < t2: 
		partido.terminado = True
		partido.fin = t2
		if partido.estadoTorneo == "1":
			partido.jugador2_marcador = -1 # -1 indica "no presentado"
		else:
			partido.jugador1_marcador = -1 # -1 indica "no presentado"
		fPartidoAnotarResultado(partido)
		return		
	if partido.pausa: # estaba en pausa y la pausa ha acabado
		s = diffTimeSec(partido.finDePausa, t2)
		if s > 0: # estaba en pausa y la pausa ha acabado
			partido.pausa = False
			partido.pelota_x = 0
			partido.pelota_y = 0
			partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion
			#print("pausa acabada")
			return
	if partido.pausa:
		partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion
		return
	#print("mover pelota")
	t1 = partido.pelota_actualizacion
	s = diffTimeSec(t1, t2)
	# y
	new_y = partido.pelota_y + partido.pelota_velocidad_y * s
	#print("mover pelota y=" + str(new_y))
	if new_y > max_y: # rebote en pared
		#print("rebote pared max_y")
		new_y = max_y - (new_y - max_y)
		partido.pelota_velocidad_y = -pelota_velocidad
	elif new_y < min_y: #rebote en pared
		#print("rebote pared min_y")
		new_y = min_y + (min_y - new_y)
		partido.pelota_velocidad_y = pelota_velocidad
	partido.pelota_y = new_y
	# x
	new_x = partido.pelota_x + partido.pelota_velocidad_x * s	
	#print("mover pelota x=" + str(new_x))	
	if new_x > max_x:	# consigue punto jugador 1
		#print("punto jugador 1 y pausa")
		s1 = datetime.timedelta(seconds=1)
		partido.pausa = True
		partido.finDePausa = t2 + s1
		partido.jugador1_marcador = partido.jugador1_marcador + 1
		partido.pelota_x = 0 # la pelota vuelve al centro pero conserva su velociad
		partido.pelota_y = 0
		if partido.jugador1_marcador >= max_puntuacion:
			partido.terminado = True
			partido.fin = t2
			fPartidoAnotarResultado(partido)
		partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion
		return
	elif new_x < min_x:	# consigue punto jugador 2
		#print("punto jugador 2 y pausa")
		s1 = datetime.timedelta(seconds=1)
		partido.pausa = True
		partido.finDePausa = t2 + s1
		partido.jugador2_marcador = partido.jugador2_marcador + 1
		partido.pelota_x = 0 # la pelota vuelve al centro pero conserva su velociad
		partido.pelota_y = 0
		if partido.jugador2_marcador >= max_puntuacion:
			partido.terminado = True
			partido.fin = t2
			fPartidoAnotarResultado(partido)
		partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion
		return
	partido.pelota_x = new_x # actualiza de momento
	#print("probar si pelota toca raquetas")
	if fJugador1TocaPelota(partido):
		if new_x < jugador1_rebote_raqueta:
			#print("toca jugador 1")
			new_x = jugador1_rebote_raqueta + (jugador1_rebote_raqueta - new_x)
			partido.pelota_velocidad_x = pelota_velocidad # rebote en raqueta
	if fJugador2TocaPelota(partido):
		if new_x > jugador2_rebote_raqueta:
			#print("toca jugador 2")
			new_x = jugador2_rebote_raqueta - (new_x - jugador2_rebote_raqueta)
			partido.pelota_velocidad_x = - pelota_velocidad # rebote en raqueta
	partido.pelota_x = new_x
	partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion

# mensajeStatus = idPartido;myLanguage
def fEnviarStatus(mensajeStatus):
	aMensajeStatus = mensajeStatus.split(";")
	idPartido = int(aMensajeStatus[0])
	myLanguage = aMensajeStatus[1]
	#print(idPartido)
	try:
		partido = Partido_enJuego.objects.get(id=idPartido) 
	except Partido_enJuego.DoesNotExist:
		#print("error al buscar partido")
		return
	#print("mover")
	fMoverPelota(partido) # cambia pelota_actualizacion
	fMoverJugador1(partido)
	fMoverJugador2(partido)
	partido.save()
	activate(myLanguage)
	status = "pcxy," + str(int(partido.pelota_x)) + "," + str(int(partido.pelota_y)) + ";"
	status = status + "j1cy," + str(int(partido.jugador1_y)) + ";"
	status = status + "j2cy," + str(int(partido.jugador2_y)) + ";"
	if partido.pausa:
		status = status + "j1m," + str(partido.jugador1_marcador) + ";"
		status = status + "j2m," + str(partido.jugador2_marcador) + ";"
	if not partido.empezado:
		status =	status + "e," +	_("Waiting player 2") + ";"
		if partido.tipo == "T":
			status = status + "j1n," + partido.jugador1.username + ";"
			status = status + "j2n," + partido.jugador2.username + ";"
		else: # "R"
			status = status + "j1n," + partido.jugador1.username + ";"
	else:
		t2 = datetime.datetime.now()
		t1 = partido.comienzo
		s = diffTimeSec(t1, t2)
		if s<2:
			# los nombre sirven especialmente para la vista del jugador que acaba de entrar
			status =	status + "j1n," + partido.jugador1.username + ";"
			status =	status + "j2n," + partido.jugador2.username + ";"
			status = status + "e," + _("Playing") + ";"
	if partido.terminado:
		status =	status + "j1m," + str(partido.jugador1_marcador) + ";"
		status =	status + "j2m," + str(partido.jugador2_marcador) + ";"
		status = status + "e," + _("Match over") + ";"
		status = status + "stop;"
	return status

def fun_keys(request): # process aj_keys
	if not request.user.is_authenticated:
		return
	mensajeKey = request.POST.get('mensaje') # mensajeKey = idPartido + ";" + numJugador + ";" + key # numJugador 1 o 2 (izq o der)
	#print("mensajeKey: idPartido;numJugador;key=" + mensajeKey + "*****************************************")
	fRecibirKey(mensajeKey)
	return JsonResponse({}, status=200)

def fun_status(request): # process aj_status
	if not request.user.is_authenticated:
		return
	mensajeStatus = request.POST.get('mensaje') # mensajeStatus = idPartido;myLanguage
	#print("mensajeStatus: idPartido=" + mensajeStatus)
	strStatus = fEnviarStatus(mensajeStatus)
	print("back: " + strStatus) # !!!!!!
	return JsonResponse({"mensaje": strStatus}, status=200)

def fun_arranque_torneo(request): #arranque torneo
	if not request.user.is_authenticated:
		return redirect('home')
	currentUser = request.user
	dd = torneo_jugar(currentUser.id)
	# dd  = { 'ok': True, 'idTorneo': idTorneo, 'fase': fase, 'idJugador1': idJugador1, 'idJugador2': idJugador2 }
	if not dd['ok'] :
		return redirect('home')
	activate_language(request)
	if currentUser.id == dd['idJugador1']:
		numJugador = 1
		strOtroJugador = "2"
	else:
		numJugador = 2
		strOtroJugador = "1"
	partido_existe = True
	try:
		partido = Partido_enJuego.objects.get(tipo="T", idTorneo=dd['idTorneo'], nFaseTorneo=dd['fase'], estadoTorneo=strOtroJugador)
		# busca el primer partido enJuego que cumple las condiciones
		# los estados en caso de torneo son: "0": sin jugadores, "1": jugador 1 dentro, "2": jugador 2 dentro, "A": ambos jugadores dentro
	except Partido_enJuego.DoesNotExist:
		partido_existe = False
	if partido_existe: #
		print("partido de torneo encontrado")
		t2 = datetime.datetime.now()
		s1 = datetime.timedelta(seconds=1)
		partido.estadoTorneo = "A" # ambos jugadores dentro
		partido.empezado = True
		partido.comienzo = t2
		partido.pausa = True
		partido.finDePausa = t2 + s1
		partido.pelota_velocidad_y = pelota_velocidad
		partido.pelota_velocidad_x = pelota_velocidad
		partido.save()
		idPartido = partido.id
	else:
		print("partido de torneo nuevo")
		partido = Partido_enJuego() #crea nuevo partido (sin arrancar) y coloca el primer jugador
		partido.setDateTimes()
		partido.tipo = "T"
		partido.idTorneo = dd['idTorneo']
		partido.nFaseTorneo = dd['fase']
		partido.estadoTorneo = str(numJugador)		
		partido.limiteTiempoTorneo = dd['limiteTiempoTorneo']
		partido.limiteTiempoConUnJugador = dd['limiteTiempoConUnJugador']
		partido.jugador1 = User.objects.get(id=dd['idJugador1'])
		partido.jugador2 = User.objects.get(id=dd['idJugador2'])		
		partido.save()
		idPartido = partido.id
	myLanguage = request.session.get('myLanguage')
	if myLanguage is None:
		myLanguage = request.LANGUAGE_CODE
	mycontext = {
		'idPartido': idPartido,
		'numJugador': numJugador, 
		'myLanguage': myLanguage,
	}
	# numJugador: 1 = izq, 2 = der
	return render(request, 'partidos/pantallaPong_t.html', mycontext)
	# enviar el html-javascript que atiende el partido cambiando idPartido, numJugador
	
def fun_arranque_rapido(request): # arranque de partido rápido
	if not request.user.is_authenticated:
		return redirect('home')
	activate_language(request)
	currentUser = request.user
	idJugador = currentUser.id
	while True:
		partidoConUnJugador = True
		try:
			partido = Partido_enJuego.objects.get(tipo="R", empezado=False, desconectado=False) #busca el primer enJuego que cumple las condiciones
			# busca el primer partido rápido, no empezado y no desconectado
			# que es lo mismo que un partido rápido con un jugador (el 1 a la izq)
		except Partido_enJuego.DoesNotExist:
			partidoConUnJugador = False
			break # no hay partido rápido con un jugador
		if partidoConUnJugador:
			t2 = datetime.datetime.now()
			t1 = partido.pelota_actualizacion
			s = diffTimeSec(t1, t2)
			if s > 2: # si no se actualiza la pelota debe ser por desconexion
				partido.desconectado = True
				partidoConUnJugador = False # este partido no es ya que lo acabo de desconectar, puede ser el siguiente del while
				partido.save()
			else:
				break # encontrado partido rápido con un jugador
	# hay dos casos partido rápido con un jugador encontrado o no
	if partidoConUnJugador: # se encontró un partido rápido sin empezar -- con un solo jugador
		t2 = datetime.datetime.now()
		s1 = datetime.timedelta(seconds=1)
		partido.jugador2 = currentUser # se coloca el segundo jugador y se arranca
		partido.empezado = True
		partido.comienzo = t2
		partido.pausa = True
		partido.finDePausa = t2 + s1
		partido.pelota_velocidad_y = pelota_velocidad
		partido.pelota_velocidad_x = pelota_velocidad
		partido.save()
		idPartido = partido.id
		numJugador = 2
	else:
		partido = Partido_enJuego() #crea nuevo partido (sin arrancar) y coloca el primer jugador
		partido.tipo = "R" # rápido
		partido.setDateTimes()
		partido.jugador1 = currentUser # se coloca el primer jugador
		partido.save()
		idPartido = partido.id
		numJugador = 1
	myLanguage = request.session.get('myLanguage')
	if myLanguage is None:
		myLanguage = request.LANGUAGE_CODE
	mycontext = {
		'idPartido': idPartido,
		'numJugador': numJugador, # 1: izq, 2: der
		'myLanguage': myLanguage,
	}
	return render(request, 'partidos/pantallaPong_t.html', mycontext)
	# enviar el html-javascript que atiende el partido cambiando idPartido, numJugador

def partidos_mlist(request):
	activate_language(request)
	user = request.user
	partidos2 = Partido_historia.objects.filter(Q(jugador1=user) | Q(jugador2=user)).annotate(duracion=F('fin') - F('comienzo'))
	context = {'partidos': partidos2, }
	return render(request, 'partidos/partidos_mlist_t.html', context)

def partidos_list(request):
	activate_language(request)
	partidos2 = Partido_historia.objects.all().annotate(duracion=F('fin') - F('comienzo'))
	context = {'partidos': partidos2, }
	return render(request, 'partidos/partidos_list_t.html', context)
