from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime

from .models import Cita, HORARIOS
from .forms import CitaForm

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
MESES = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]


def inicio_semana(fecha):
    return fecha - datetime.timedelta(days=fecha.weekday())


@login_required
def agenda_semanal(request):
    hoy = timezone.now().date()

    semana_str = request.GET.get('semana')
    if semana_str:
        try:
            lunes = datetime.date.fromisoformat(semana_str)
        except ValueError:
            lunes = inicio_semana(hoy)
    else:
        lunes = inicio_semana(hoy)

    sabado = lunes + datetime.timedelta(days=5)
    semana_anterior = lunes - datetime.timedelta(weeks=1)
    semana_siguiente = lunes + datetime.timedelta(weeks=1)

    dias = [lunes + datetime.timedelta(days=i) for i in range(6)]

    citas_qs = Cita.objects.filter(fecha__range=(lunes, sabado)).select_related('paciente')
    citas_map = {(str(c.fecha), c.hora): c for c in citas_qs}

    grilla = []
    for hora, _ in HORARIOS:
        fila = {'hora': hora, 'celdas': []}
        for dia in dias:
            cita = citas_map.get((str(dia), hora))
            fila['celdas'].append({'fecha': dia, 'hora': hora, 'cita': cita})
        grilla.append(fila)

    context = {
        'dias': dias,
        'dias_nombres': DIAS_SEMANA,
        'grilla': grilla,
        'lunes': lunes,
        'sabado': sabado,
        'hoy': hoy,
        'semana_anterior': semana_anterior,
        'semana_siguiente': semana_siguiente,
        'meses': MESES,
    }
    return render(request, 'citas/agenda.html', context)


@login_required
def cita_nueva(request):
    fecha = request.GET.get('fecha', '')
    hora = request.GET.get('hora', '')

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save()
            messages.success(request, f'Cita agendada: {cita.paciente} — {cita.fecha.strftime("%d/%m/%Y")} {cita.hora}')
            return redirect(f'/agenda/?semana={inicio_semana(cita.fecha).isoformat()}')
    else:
        form = CitaForm(fecha=fecha, hora=hora)

    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Nueva Cita', 'fecha': fecha, 'hora': hora})


@login_required
def cita_editar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada correctamente.')
            return redirect(f'/agenda/?semana={inicio_semana(cita.fecha).isoformat()}')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Editar Cita', 'cita': cita})


@login_required
def cita_confirmar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    cita.estado = 'confirmada'
    cita.save()
    messages.success(request, f'Cita de {cita.paciente} confirmada.')
    next_url = request.POST.get('next', request.GET.get('next', 'home'))
    return redirect(next_url)


@login_required
def cita_cancelar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    semana = inicio_semana(cita.fecha).isoformat()
    next_url = request.POST.get('next', request.GET.get('next', ''))
    cita.delete()
    messages.success(request, 'Cita eliminada y turno liberado.')
    if next_url:
        return redirect(next_url)
    return redirect(f'/agenda/?semana={semana}')
