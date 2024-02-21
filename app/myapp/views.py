# coding: utf8

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import Context, Template

#from django.contrib.auth import authenticate, login, logout 

import datetime

"""
def mi_html1(request):
    return render(request, 'myapp/hola.html')
    
#render(request, template , context)
    
def mi_html2(request):
    return render(request, 'myapp/pantallaPong.html')
 
def mi_html3(request):
    mytemplate = get_template("myapp/hola.html")
    return HttpResponse(mytemplate.render()) 

def mi_html4(request):
    mytemplate = get_template("myapp/pantallaPong_t.html")
    mycontext = {
    'idPartido': 333,
    'numJugador': 2,
    }
    return HttpResponse(mytemplate.render(mycontext))

def mi_html5(request):
    mycontext = {
    'idPartido': 333,
    'numJugador': 2,
    }
    return render(request, "myapp/pantallaPong_t.html", mycontext)
    
"""

# code base

from .models import Partido

# constantes globales

campo = { "ancho": 800, "alto": 400  }
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
pelota_velocidad = 60

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
  #print("j1 seconds="  + str(s))
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
  #print("j2 seconds="  + str(s))
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
    partido = Partido.objects.get(id=idPartido)
  except Partido.DoesNotExist:
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

def fMoverPelota(partido):
  t2 = datetime.datetime.now()
  if partido.pausa and partido.finDePausa <= t2: # estaba en pausa y la pausa ha acabado
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
  if new_x > max_x:  # consigue punto jugador 1
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
    partido.pelota_actualizacion = t2 # en todos los casos se fija pelota_actualizacion
    return
  elif new_x < min_x:  # consigue punto jugador 2
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


# mensajeStatus = idPartido
def fEnviarStatus(mensajeStatus):
  idPartido = int(mensajeStatus)
  try:
    partido = Partido.objects.get(id=idPartido) 
  except Partido.DoesNotExist:
    return
  # partido = Partido.objects.all()[idPartido] # busca el partido en la BD # mal la posicion no es el id
  fMoverPelota(partido) # cambia pelota_actualizacion
  fMoverJugador1(partido)
  fMoverJugador2(partido)
  partido.save()
  status = "pcxy," + str(int(partido.pelota_x)) + "," + str(int(partido.pelota_y)) + ";"
  status =  status + "j1cy," + str(int(partido.jugador1_y)) + ";"
  status =  status + "j2cy," + str(int(partido.jugador2_y)) + ";"
  if partido.pausa:
    status =  status + "j1m," + str(partido.jugador1_marcador) + ";"
    status =  status + "j2m," + str(partido.jugador2_marcador) + ";"
  if not partido.empezado:
    status =  status + "e," +  "Esperando jugador 2" + ";"
    status =  status + "j1n," + partido.jugador1_nombre + ";"
  else:
    t2 = datetime.datetime.now()
    t1 = partido.comienzo
    s = diffTimeSec(t1, t2)
    if s<2:
      status =  status + "j1n," + partido.jugador1_nombre + ";"
      status =  status + "j2n," + partido.jugador2_nombre + ";"
      status = status + "e," + "Jugando" + ";"
  if partido.terminado:
    status =  status + "j1m," + str(partido.jugador1_marcador) + ";"
    status =  status + "j2m," + str(partido.jugador2_marcador) + ";"
    status = status + "e," + "Terminado" + ";"
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
  mensajeStatus = request.POST.get('mensaje') # mensajeStatus = idPartido
  #print("mensajeStatus: idPartido=" + mensajeStatus)
  strStatus = fEnviarStatus(mensajeStatus)
  #print("back: " + strStatus)
  return JsonResponse({"mensaje": strStatus}, status=200)

def fun_arranque(request): # process url_arranque
  #idJugador = request.GET.get('idJugador') # antiguo
  currentUser = request.user
  # idJugador = currentUser.id
  nombreJugador = currentUser.username
  #print(nombreJugador) 
  if nombreJugador is None:
    return redirect('home')
  while True:
    partidoConUnJugador = True
    try:
      partido = Partido.objects.get(empezado=False, desconectado=False) #busca el primer partido que cumple las dos condiciones
      # busca el primer partido no empezado y no desconectado
      # que es lo mismo que un partido con un jugador
    except Partido.DoesNotExist:
      partidoConUnJugador = False
      break # no hay partido con un jugador
    if partidoConUnJugador:
      t2 = datetime.datetime.now()
      t1 = partido.pelota_actualizacion
      s = diffTimeSec(t1, t2)
      if s > 2: # si no se actualiza la pelota debe ser por desconexion
        partido.desconectado = True
        partidoConUnJugador = False # este partido no es ya que lo acabo de desconectar, puede ser el siguiente del while
        partido.save()
      else:
        break # encontrado partido con un jugador
  if partidoConUnJugador: # se encontro un partido sin empezar -- con un solo jugador
      t2 = datetime.datetime.now()
      s1 = datetime.timedelta(seconds=1)
      partido.jugador2_nombre = nombreJugador # se coloca el segundo jugador y se arranca
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
      partido = Partido() #crea nuevo partido (sin arrancar) y coloca el primer jugador
      partido.setDateTimes()
      partido.jugador1_nombre = nombreJugador # se coloca el primer jugador
      partido.save()
      idPartido = partido.id
      numJugador = 1
  mycontext = {
    'idPartido': idPartido,
    'numJugador': numJugador,
  }
  return render(request, 'myapp/pantallaPong_t.html', mycontext)
  # enviar el html-javascript que atiende el partido cambiando idPartido, numJugador
