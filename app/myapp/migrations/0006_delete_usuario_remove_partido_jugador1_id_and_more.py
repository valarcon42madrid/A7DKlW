# Generated by Django 5.0.1 on 2024-02-11 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_partido_comienzo_alter_partido_findepausa_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Usuario',
        ),
        migrations.RemoveField(
            model_name='partido',
            name='jugador1_id',
        ),
        migrations.RemoveField(
            model_name='partido',
            name='jugador2_id',
        ),
        migrations.AddField(
            model_name='partido',
            name='jugador1_nombre',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='partido',
            name='jugador2_nombre',
            field=models.CharField(default='', max_length=150),
        ),
    ]