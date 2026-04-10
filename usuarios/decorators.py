from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def permiso_requerido(permiso):
    """Verifica que el usuario tenga el permiso dado en su perfil."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                perfil = request.user.perfil
            except Exception:
                messages.error(request, 'Tu cuenta no tiene un perfil configurado.')
                return redirect('home')
            if not perfil.tiene_permiso(permiso):
                messages.error(request, 'No tienes permiso para realizar esta acción.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_admin(view_func):
    """Solo administradores pueden acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if not request.user.perfil.es_admin():
                messages.error(request, 'Solo los administradores pueden acceder a esta sección.')
                return redirect('home')
        except Exception:
            messages.error(request, 'Tu cuenta no tiene un perfil configurado.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
