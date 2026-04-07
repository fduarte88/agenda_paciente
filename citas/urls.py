from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda_semanal, name='agenda'),
    path('agenda/nueva/', views.cita_nueva, name='cita_nueva'),
    path('agenda/<int:pk>/editar/', views.cita_editar, name='cita_editar'),
    path('agenda/<int:pk>/cancelar/', views.cita_cancelar, name='cita_cancelar'),
]
