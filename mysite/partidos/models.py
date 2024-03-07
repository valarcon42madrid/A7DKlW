from django.db import models
from django.contrib.auth.models import User
import datetime

# Se anaden los modelos de datos -- similar a tablas de base de datos
# por defecto anade id a cada tabla

# jugador1 a la izquierda -- jugador2 a la derecha
# coordenadas: 0, 0 centro del campo, x hacia derecha, y hacia abajo

class Partido_enJuego(models.Model):
  jugador1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'pj_user_jugador1')
  jugador2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'pj_user_jugador2')
  empezado = models.BooleanField(default=False) # si true partido empezado
  terminado = models.BooleanField(default=False) # si true partido terminado
  comienzo = models.DateTimeField(null=True, blank=True, default=None) # comienzo del partido
  fin = models.DateTimeField(null=True, blank=True, default=None) # final del partido
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

class Partido_historia(models.Model):
  jugador1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'ph_user_jugador1')
  jugador2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'ph_user_jugador2')
  jugador1_marcador = models.IntegerField(default=0)  # marcador de puntos
  jugador2_marcador = models.IntegerField(default=0) 
  comienzo = models.DateTimeField(null=True, blank=True, default=None) # comienzo del partido
  fin = models.DateTimeField(null=True, blank=True, default=None) # final del partido
  ordering = ['-comienzo']

