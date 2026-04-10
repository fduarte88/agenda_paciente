from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    ROL_CHOICES = [
        ('admin',    'Administrador'),
        ('operador', 'Operador'),
    ]

    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default='operador')
    genero = models.CharField('Género', max_length=1, choices=GENERO_CHOICES, default='M')

    # Permisos granulares para operadores
    puede_ver_pacientes     = models.BooleanField('Ver pacientes',      default=True)
    puede_crear_pacientes   = models.BooleanField('Crear pacientes',    default=True)
    puede_editar_pacientes  = models.BooleanField('Editar pacientes',   default=True)

    puede_ver_agenda        = models.BooleanField('Ver agenda',         default=True)
    puede_crear_citas       = models.BooleanField('Crear citas',        default=True)
    puede_editar_citas      = models.BooleanField('Editar citas',       default=True)
    puede_cancelar_citas    = models.BooleanField('Cancelar citas',     default=True)

    puede_ver_usuarios      = models.BooleanField('Ver usuarios',       default=False)
    puede_gestionar_usuarios= models.BooleanField('Gestionar usuarios', default=False)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'

    def es_admin(self):
        return self.rol == 'admin'

    def tiene_permiso(self, permiso):
        """Los admins tienen todos los permisos siempre."""
        if self.es_admin():
            return True
        return getattr(self, permiso, False)


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
