from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pacientes.models import Paciente
from citas.models import Cita


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    from django.utils import timezone
    hoy = timezone.now().date()
    total_pacientes = Paciente.objects.count()
    proximas_citas = (
        Cita.objects
        .filter(fecha__gte=hoy)
        .select_related('paciente')
        .order_by('fecha', 'hora')[:15]
    )
    return render(request, 'accounts/home.html', {
        'total_pacientes': total_pacientes,
        'proximas_citas': proximas_citas,
        'hoy': hoy,
    })
