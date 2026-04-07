from django import forms
from .models import Cita, HORARIOS
from pacientes.models import Paciente


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'fecha', 'hora', 'estado', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'paciente': 'Paciente',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'estado': 'Estado',
            'notas': 'Notas (opcional)',
        }

    def __init__(self, *args, **kwargs):
        fecha = kwargs.pop('fecha', None)
        hora = kwargs.pop('hora', None)
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.order_by('apellido', 'nombre')
        self.fields['paciente'].empty_label = '— Selecciona un paciente —'
        if fecha:
            self.fields['fecha'].initial = fecha
        if hora:
            self.fields['hora'].initial = hora

    def clean(self):
        cleaned = super().clean()
        fecha = cleaned.get('fecha')
        hora = cleaned.get('hora')
        if fecha and hora:
            qs = Cita.objects.filter(fecha=fecha, hora=hora)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe una cita agendada para ese horario.')
        return cleaned
