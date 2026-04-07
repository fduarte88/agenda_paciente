from django import forms
from .models import Cita, HORARIOS
from pacientes.models import Paciente

DATE_WIDGET_ATTRS = {
    'placeholder': 'dd/mm/aaaa',
    'autocomplete': 'off',
    'class': 'date-mask',
    'maxlength': '10',
}


class CitaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.TextInput(attrs=DATE_WIDGET_ATTRS),
        label='Fecha',
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
    )

    class Meta:
        model = Cita
        fields = ['paciente', 'fecha', 'hora', 'estado', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'paciente': 'Paciente',
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
            # fecha viene como yyyy-mm-dd desde la URL, convertir a dd/mm/aaaa
            try:
                from datetime import date
                parts = fecha.split('-')
                self.fields['fecha'].initial = f'{parts[2]}/{parts[1]}/{parts[0]}'
            except Exception:
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
