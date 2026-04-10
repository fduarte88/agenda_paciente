from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Dejar vacío para no cambiar'}),
        required=False,
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'is_active']
        labels = {
            'first_name': 'Nombre',
            'last_name':  'Apellido',
            'username':   'Usuario',
            'email':      'Correo electrónico',
            'is_active':  'Cuenta activa',
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirmar_password')
        if p1 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'rol', 'genero',
            'puede_ver_pacientes', 'puede_crear_pacientes', 'puede_editar_pacientes',
            'puede_ver_agenda', 'puede_crear_citas', 'puede_editar_citas', 'puede_cancelar_citas',
            'puede_ver_usuarios', 'puede_gestionar_usuarios',
        ]
        labels = {
            'rol': 'Rol',
            'genero': 'Género',
            'puede_ver_pacientes':      'Ver pacientes',
            'puede_crear_pacientes':    'Crear pacientes',
            'puede_editar_pacientes':   'Editar pacientes',
            'puede_ver_agenda':         'Ver agenda',
            'puede_crear_citas':        'Crear citas',
            'puede_editar_citas':       'Editar / confirmar citas',
            'puede_cancelar_citas':     'Cancelar citas',
            'puede_ver_usuarios':       'Ver usuarios',
            'puede_gestionar_usuarios': 'Crear / editar usuarios',
        }
