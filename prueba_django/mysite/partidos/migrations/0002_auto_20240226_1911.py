# Generated by Django 3.2.5 on 2024-02-26 19:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partidos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partido_enJuego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empezado', models.BooleanField(default=False)),
                ('terminado', models.BooleanField(default=False)),
                ('comienzo', models.DateTimeField(blank=True, default=None, null=True)),
                ('fin', models.DateTimeField(blank=True, default=None, null=True)),
                ('desconectado', models.BooleanField(default=False)),
                ('jugador1_marcador', models.IntegerField(default=0)),
                ('jugador2_marcador', models.IntegerField(default=0)),
                ('pausa', models.BooleanField(default=False)),
                ('finDePausa', models.DateTimeField(blank=True, default=None, null=True)),
                ('pelota_actualizacion', models.DateTimeField(blank=True, default=None, null=True)),
                ('pelota_x', models.FloatField(default=0)),
                ('pelota_y', models.FloatField(default=0)),
                ('pelota_velocidad_x', models.FloatField(default=0)),
                ('pelota_velocidad_y', models.FloatField(default=0)),
                ('jugador1_actualizacion', models.DateTimeField(blank=True, default=None, null=True)),
                ('jugador1_y', models.FloatField(default=0)),
                ('jugador1_velocidad_y', models.FloatField(default=0)),
                ('jugador2_actualizacion', models.DateTimeField(blank=True, default=None, null=True)),
                ('jugador2_y', models.FloatField(default=0)),
                ('jugador2_velocidad_y', models.FloatField(default=0)),
                ('jugador1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pj_user_jugador1', to=settings.AUTH_USER_MODEL)),
                ('jugador2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pj_user_jugador2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Partido_historia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jugador1_marcador', models.IntegerField(default=0)),
                ('jugador2_marcador', models.IntegerField(default=0)),
                ('comienzo', models.DateTimeField(blank=True, default=None, null=True)),
                ('fin', models.DateTimeField(blank=True, default=None, null=True)),
                ('jugador1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ph_user_jugador1', to=settings.AUTH_USER_MODEL)),
                ('jugador2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ph_user_jugador2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Partido',
        ),
    ]
