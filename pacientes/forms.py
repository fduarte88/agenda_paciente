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
        fields = ['nombre', 'apellido', 'fecha_nacimiento', 'nombre_acudiente', 'telefono_acudiente', 'parentesco']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'nombre_acudiente': 'Nombre del acudiente',
            'telefono_acudiente': 'Teléfono de contacto',
            'parentesco': 'Parentesco',
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

    def clean_nombre_acudiente(self):
        return self.cleaned_data['nombre_acudiente'].strip().title()
