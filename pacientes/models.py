from django.db import models
from django.utils import timezone


class Paciente(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    fecha_nacimiento = models.DateField('Fecha de nacimiento')
    nombre_madre = models.CharField('Nombre de la madre', max_length=200, blank=True, default='')
    telefono_madre = models.CharField('Teléfono de la madre', max_length=20, blank=True, default='')
    nombre_padre = models.CharField('Nombre del padre', max_length=200, blank=True, default='')
    telefono_padre = models.CharField('Teléfono del padre', max_length=20, blank=True, default='')
    nombre_tutor = models.CharField('Nombre del tutor', max_length=200, blank=True, default='')
    telefono_tutor = models.CharField('Teléfono del tutor', max_length=20, blank=True, default='')
    escolaridad = models.CharField('Escolaridad', max_length=100, blank=True, default='')
    direccion = models.CharField('Dirección', max_length=300, blank=True, default='')
    historial_clinico = models.TextField('Historial clínico', blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def edad(self):
        hoy = timezone.now().date()
        nac = self.fecha_nacimiento
        anos = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
        meses = (hoy.month - nac.month - (hoy.day < nac.day)) % 12
        if anos == 0:
            return f'{meses} mes{"es" if meses != 1 else ""}'
        if meses == 0:
            return f'{anos} año{"s" if anos != 1 else ""}'
        return f'{anos} año{"s" if anos != 1 else ""} y {meses} mes{"es" if meses != 1 else ""}'
