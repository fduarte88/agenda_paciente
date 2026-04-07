from django.db import models
from pacientes.models import Paciente

HORARIOS = [
    ('08:00', '08:00'), ('08:40', '08:40'), ('09:20', '09:20'),
    ('10:00', '10:00'), ('10:40', '10:40'), ('11:20', '11:20'),
    ('12:00', '12:00'), ('12:40', '12:40'), ('13:20', '13:20'),
    ('14:00', '14:00'), ('14:40', '14:40'), ('15:20', '15:20'),
    ('16:00', '16:00'), ('16:40', '16:40'), ('17:20', '17:20'),
    ('18:00', '18:00'), ('18:40', '18:40'), ('19:20', '19:20'),
]

ESTADO_CHOICES = [
    ('pendiente',  'Pendiente'),
    ('confirmada', 'Confirmada'),
    ('cancelada',  'Cancelada'),
]


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField('Fecha')
    hora = models.CharField('Hora', max_length=5, choices=HORARIOS)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField('Notas', blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora']
        unique_together = ['fecha', 'hora']  # un paciente por franja horaria

    def __str__(self):
        return f'{self.fecha} {self.hora} — {self.paciente}'
