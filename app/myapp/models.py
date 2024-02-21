from django.db import models
import datetime

# Se anaden los modelos de datos -- similar a tablas de base de datos
# por defecto anade id a cada tabla

"""
class Usuario(models.Model):
  TIPO = { "J": "Jugador", "A": "Administrador", }
  nombre = models.CharField(max_length=255)
  clave = models.CharField(max_length=255)
  tipo = models.CharField(max_length=1, choices=TIPO)
  #class Meta:
  #  app_label = 'myapp' # add app
"""

# jugador1 a la izquierda -- jugador2 a la derecha
# coordenadas: 0, 0 centro del campo, x hacia derecha, y hacia abajo

class Partido(models.Model):
  jugador1_nombre = models.CharField(default="", max_length=150)
  jugador2_nombre = models.CharField(default="", max_length=150)
  empezado = models.BooleanField(default=False) # si true partido empezado
  terminado = models.BooleanField(default=False) # si true partido terminado
  comienzo = models.DateTimeField(null=True, blank=True, default=None) # comienzo del partido
  fin = models.DateTimeField(null=True, default=None) # final del partido
  desconectado = models.BooleanField(default=False) # si los clientes dejan de pedir el estado durante un tiempo se desconecta
  jugador1_marcador = models.IntegerField(default=0)  # marcador de puntos
  jugador2_marcador = models.IntegerField(default=0) 
  pausa = models.BooleanField(default=False) # si true partido en pausa # si se marca un punto se espera 1 s antes de seguir (saque)
  finDePausa = models.DateTimeField(null=True, blank=True, default=None) # si esta en pausa este es el momento que se quitara la pausa
  pelota_actualizacion = models.DateTimeField(null=True, blank=True, default=None)
  pelota_x = models.FloatField(default=0)
  pelota_y = models.FloatField(default=0)
  pelota_velocidad_x = models.FloatField(default=0)
  pelota_velocidad_y = models.FloatField(default=0)  
  jugador1_actualizacion = models.DateTimeField(null=True, blank=True, default=None)
  jugador1_y = models.FloatField(default=0)
  jugador1_velocidad_y = models.FloatField(default=0)  
  jugador2_actualizacion = models.DateTimeField(null=True, blank=True, default=None)
  jugador2_y = models.FloatField(default=0)
  jugador2_velocidad_y = models.FloatField(default=0)
  def setDateTimes(self):
    t = datetime.datetime.now()
    self.pelota_actualizacion = t
    self.jugador1_actualizacion = t
    self.jugador2_actualizacion = t
  #class Meta:
  #  app_label = 'myapp' # add app


"""
If a model is defined outside of applications in INSTALLED_APPS, it must declare which app  it belongs to:
class x(models.Model):
  class Meta:
      app_label = 'myapp' # add app name here

"""