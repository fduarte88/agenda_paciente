from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paciente
from .forms import PacienteForm


@login_required
def paciente_nuevo(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} registrado exitosamente.')
            return redirect('paciente_lista')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Registrar Paciente'})


@login_required
def paciente_lista(request):
    q = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.all()
    if q:
        pacientes = pacientes.filter(
            nombre__icontains=q
        ) | pacientes.filter(
            apellido__icontains=q
        )
        pacientes = pacientes.distinct()
    return render(request, 'pacientes/lista.html', {'pacientes': pacientes, 'q': q})


@login_required
def paciente_detalle(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    return render(request, 'pacientes/detalle.html', {'paciente': paciente})


@login_required
def paciente_editar(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} actualizado.')
            return redirect('paciente_lista')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Editar Paciente', 'paciente': paciente})
