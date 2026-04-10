from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Perfil
from .forms import UsuarioForm, PerfilForm
from .decorators import permiso_requerido, solo_admin


@login_required
@permiso_requerido('puede_ver_usuarios')
def usuario_lista(request):
    usuarios = User.objects.select_related('perfil').order_by('last_name', 'first_name')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
@permiso_requerido('puede_gestionar_usuarios')
def usuario_nuevo(request):
    if request.method == 'POST':
        form_user = UsuarioForm(request.POST)
        form_perfil = PerfilForm(request.POST)
        if form_user.is_valid() and form_perfil.is_valid():
            user = form_user.save(commit=False)
            password = form_user.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                messages.error(request, 'Debes ingresar una contraseña para el nuevo usuario.')
                return render(request, 'usuarios/form.html', {
                    'form_user': form_user, 'form_perfil': form_perfil, 'titulo': 'Nuevo Usuario'
                })
            user.save()
            perfil = user.perfil
            form_perfil_data = form_perfil.cleaned_data
            for field, value in form_perfil_data.items():
                setattr(perfil, field, value)
            perfil.save()
            messages.success(request, f'Usuario {user.username} creado correctamente.')
            return redirect('usuario_lista')
    else:
        form_user = UsuarioForm()
        form_perfil = PerfilForm()
    return render(request, 'usuarios/form.html', {
        'form_user': form_user, 'form_perfil': form_perfil, 'titulo': 'Nuevo Usuario'
    })


@login_required
@permiso_requerido('puede_gestionar_usuarios')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    # No permitir editar otro admin si no eres admin
    if usuario.perfil.es_admin() and not request.user.perfil.es_admin():
        messages.error(request, 'No puedes editar a un administrador.')
        return redirect('usuario_lista')

    if request.method == 'POST':
        form_user = UsuarioForm(request.POST, instance=usuario)
        form_perfil = PerfilForm(request.POST, instance=usuario.perfil)
        if form_user.is_valid() and form_perfil.is_valid():
            user = form_user.save(commit=False)
            password = form_user.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            form_perfil.save()
            messages.success(request, f'Usuario {user.username} actualizado.')
            return redirect('usuario_lista')
    else:
        form_user = UsuarioForm(instance=usuario)
        form_perfil = PerfilForm(instance=usuario.perfil)
    return render(request, 'usuarios/form.html', {
        'form_user': form_user, 'form_perfil': form_perfil,
        'titulo': 'Editar Usuario', 'usuario': usuario
    })


@login_required
@solo_admin
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('usuario_lista')
    nombre = usuario.username
    usuario.delete()
    messages.success(request, f'Usuario {nombre} eliminado.')
    return redirect('usuario_lista')
