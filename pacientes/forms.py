from django import forms
from .models import Paciente

DATE_WIDGET_ATTRS = {
    'placeholder': 'dd/mm/aaaa',
    'autocomplete': 'off',
    'class': 'date-mask',
    'maxlength': '10',
}


class PacienteForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.TextInput(attrs=DATE_WIDGET_ATTRS),
        label='Fecha de nacimiento',
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
    )

    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'fecha_nacimiento',
                  'nombre_madre', 'telefono_madre', 'nombre_padre', 'telefono_padre',
                  'nombre_tutor', 'telefono_tutor',
                  'escolaridad', 'direccion', 'historial_clinico']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'nombre_madre': 'Nombre de la madre',
            'telefono_madre': 'Número de contacto',
            'nombre_padre': 'Nombre del padre',
            'telefono_padre': 'Número de contacto',
            'nombre_tutor': 'Nombre del tutor',
            'telefono_tutor': 'Número de contacto',
            'escolaridad': 'Escolaridad',
            'direccion': 'Dirección',
            'historial_clinico': 'Historial clínico',
        }
        widgets = {
            'historial_clinico': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Motivo de consulta, diagnósticos previos, observaciones...'}),
        }

    def clean_fecha_nacimiento(self):
        from django.utils import timezone
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > timezone.now().date():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha

    def clean_nombre(self):
        return self.cleaned_data['nombre'].strip().title()

    def clean_apellido(self):
        return self.cleaned_data['apellido'].strip().title()

    def clean_nombre_madre(self):
        return self.cleaned_data['nombre_madre'].strip().title()

    def clean_nombre_padre(self):
        return self.cleaned_data['nombre_padre'].strip().title()

    def clean_nombre_tutor(self):
        return self.cleaned_data['nombre_tutor'].strip().title()
