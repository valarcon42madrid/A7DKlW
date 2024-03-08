# Generated by Django 5.0.2 on 2024-03-05 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partidos', '0002_auto_20240226_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='partido_enjuego',
            name='estadoTorneo',
            field=models.CharField(choices=[('0', 'SinJugadores'), ('1', 'Jugador1Dentro'), ('2', 'Jugador2Dentro'), ('A', 'AmbosJugadoresDentro')], default='0', max_length=1),
        ),
        migrations.AddField(
            model_name='partido_enjuego',
            name='idTorneo',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='partido_enjuego',
            name='limiteTiempoTorneo',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='partido_enjuego',
            name='nFaseTorneo',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='partido_enjuego',
            name='tipo',
            field=models.CharField(choices=[('R', 'Rapido'), ('T', 'Torneo')], default='R', max_length=1),
        ),
    ]