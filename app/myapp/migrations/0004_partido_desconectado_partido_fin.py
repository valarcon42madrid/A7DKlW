# Generated by Django 5.0.1 on 2024-02-06 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_partido_pausa'),
    ]

    operations = [
        migrations.AddField(
            model_name='partido',
            name='desconectado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partido',
            name='fin',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
