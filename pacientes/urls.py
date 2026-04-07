from django.urls import path
from . import views

urlpatterns = [
    path('pacientes/', views.paciente_lista, name='paciente_lista'),
    path('pacientes/nuevo/', views.paciente_nuevo, name='paciente_nuevo'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detalle'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_editar'),
]
