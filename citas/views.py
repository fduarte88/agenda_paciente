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

def formato_semana(lunes, sabado):
    """Ej: '06 — 11 de abril 2026' o '28 mar — 02 abr 2026' si cruza mes."""
    if lunes.month == sabado.month:
        return f'{lunes.day:02d} — {sabado.day:02d} de {MESES[sabado.month]} {sabado.year}'
    else:
        return (
            f'{lunes.day:02d} {MESES[lunes.month][:3]} — '
            f'{sabado.day:02d} {MESES[sabado.month][:3]} {sabado.year}'
        )


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
    # Por slot: priorizar cita activa sobre cancelada
    citas_map = {}
    for c in citas_qs:
        key = (str(c.fecha), c.hora)
        existente = citas_map.get(key)
        if existente is None or existente.estado == 'cancelada':
            citas_map[key] = c

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
        'titulo_semana': formato_semana(lunes, sabado),
        'num_semana': lunes.isocalendar()[1],
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
    cita.estado = 'cancelada'
    cita.save()
    messages.success(request, f'Cita de {cita.paciente} cancelada. El turno queda disponible para reagendar.')
    if next_url:
        return redirect(next_url)
    return redirect(f'/agenda/?semana={semana}')
